"""ETL: operative Datenbank Retail_OLTP -> Data Warehouse Retail_DWH (Star Schema).

Schritte:
    1. Statische Dimensionen (Store, Employee, Customer) idempotent laden
    2. Produktdimension als SCD Typ 2 (Preisänderung -> alte Version schließen,
       neue Version aktiv anlegen)
    3. Zeitdimension auf Stundenebene (Datum + Stunde)
    4. Faktentabelle Sales_Fact über Surrogate-Key-Lookups befüllen

Das Skript ist wiederholbar: bereits vorhandene Dimensionszeilen werden nicht
dupliziert. Die Faktentabelle wird vor dem Laden geleert, damit ein erneuter
Lauf keine doppelten Fakten erzeugt.

Aufruf:  python python/etl_process.py
"""

import logging
import sys
from collections import Counter
from datetime import datetime

import pyodbc

from db_config import DWH_DATABASE, OLTP_DATABASE, configure_logging, connect


def load_static_dimensions(src: pyodbc.Cursor, dwh: pyodbc.Cursor) -> None:
    """Lädt Store_Dim, Employee_Dim und Customer_Dim (nur neue Schlüssel)."""
    src.execute(
        "SELECT s.StoreID, s.StoreName, c.CountryName "
        "FROM Stores s JOIN Countries c ON s.CountryID = c.CountryID"
    )
    dwh.executemany(
        "IF NOT EXISTS (SELECT 1 FROM Store_Dim WHERE StoreID = ?) "
        "INSERT INTO Store_Dim (StoreID, StoreName, CountryName) VALUES (?, ?, ?)",
        [(r.StoreID, r.StoreID, r.StoreName, r.CountryName) for r in src.fetchall()],
    )

    src.execute(
        "SELECT e.EmployeeID, e.FullName, s.StoreName "
        "FROM Employees e JOIN Stores s ON e.StoreID = s.StoreID"
    )
    dwh.executemany(
        "IF NOT EXISTS (SELECT 1 FROM Employee_Dim WHERE EmployeeID = ?) "
        "INSERT INTO Employee_Dim (EmployeeID, FullName, StoreName) VALUES (?, ?, ?)",
        [(r.EmployeeID, r.EmployeeID, r.FullName, r.StoreName) for r in src.fetchall()],
    )

    src.execute(
        "SELECT c.CustomerID, co.CountryName "
        "FROM Customers c JOIN Countries co ON c.CountryID = co.CountryID"
    )
    dwh.executemany(
        "IF NOT EXISTS (SELECT 1 FROM Customer_Dim WHERE CustomerID = ?) "
        "INSERT INTO Customer_Dim (CustomerID, CountryName, Start_Date, IsActive) "
        "VALUES (?, ?, CAST(GETDATE() AS DATE), 1)",
        [(r.CustomerID, r.CustomerID, r.CountryName) for r in src.fetchall()],
    )
    logging.info("Statische Dimensionen geladen")


def load_product_dimension_scd2(src: pyodbc.Cursor, dwh: pyodbc.Cursor) -> None:
    """SCD Typ 2: neue Produkte anlegen, Preisänderungen historisieren."""
    dwh.execute("SELECT ProductID, CurrentPrice FROM Product_Dim WHERE IsActive = 1")
    active_prices = {row.ProductID: float(row.CurrentPrice) for row in dwh.fetchall()}

    src.execute(
        "SELECT p.ProductID, p.StockCode, p.Description, c.CategoryName, p.CurrentPrice "
        "FROM Products p JOIN Categories c ON p.CategoryID = c.CategoryID"
    )
    insert_sql = (
        "INSERT INTO Product_Dim (ProductID, StockCode, Description, CategoryName, "
        "CurrentPrice, Start_Date, IsActive) VALUES (?, ?, ?, ?, ?, CAST(GETDATE() AS DATE), 1)"
    )
    new_versions, closed = [], []
    for row in src.fetchall():
        values = (row.ProductID, row.StockCode, row.Description, row.CategoryName, row.CurrentPrice)
        current = active_prices.get(row.ProductID)
        if current is None:
            new_versions.append(values)
        elif current != float(row.CurrentPrice):
            closed.append((row.ProductID,))
            new_versions.append(values)

    dwh.executemany(
        "UPDATE Product_Dim SET IsActive = 0, End_Date = CAST(GETDATE() AS DATE) "
        "WHERE ProductID = ? AND IsActive = 1",
        closed,
    )
    dwh.executemany(insert_sql, new_versions)
    logging.info(
        "Product_Dim: %s neue Versionen, davon %s Preisänderungen (SCD 2)",
        len(new_versions), len(closed),
    )


def load_time_dimension(src: pyodbc.Cursor, dwh: pyodbc.Cursor) -> None:
    """Zeitdimension auf Stundenebene; Schlüssel ist (FullDate, Hour)."""
    src.execute("SELECT DISTINCT InvoiceDate FROM SalesHeaders")
    seen, rows = set(), []
    for (invoice_date,) in src.fetchall():
        dt: datetime = invoice_date
        key = (dt.date(), dt.hour)
        if key in seen:
            continue
        seen.add(key)
        rows.append((
            dt.date(), dt.hour,
            dt.date(), dt.year, dt.month, dt.day, dt.hour,
            (dt.month - 1) // 3 + 1, dt.isocalendar()[1], dt.strftime("%A"),
        ))
    dwh.executemany(
        "IF NOT EXISTS (SELECT 1 FROM Time_Dim WHERE FullDate = ? AND Hour = ?) "
        "INSERT INTO Time_Dim (FullDate, Year, Month, Day, Hour, Quarter, Week, Weekday) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    logging.info("Time_Dim: %s Datum/Stunden-Kombinationen", len(rows))


def surrogate_key_maps(dwh: pyodbc.Cursor) -> dict:
    """Liest alle Surrogate Keys einmal ein statt pro Faktzeile abzufragen."""
    dwh.execute("SELECT ProductID, Product_Dim_ID FROM Product_Dim WHERE IsActive = 1")
    product = dict(dwh.fetchall())
    dwh.execute("SELECT CustomerID, Customer_Dim_ID FROM Customer_Dim WHERE IsActive = 1")
    customer = dict(dwh.fetchall())
    dwh.execute("SELECT StoreID, Store_Dim_ID FROM Store_Dim")
    store = dict(dwh.fetchall())
    dwh.execute("SELECT EmployeeID, Employee_Dim_ID FROM Employee_Dim")
    employee = dict(dwh.fetchall())
    dwh.execute("SELECT FullDate, Hour, Time_Dim_ID FROM Time_Dim")
    time = {(r.FullDate, r.Hour): r.Time_Dim_ID for r in dwh.fetchall()}
    return {"product": product, "customer": customer, "store": store,
            "employee": employee, "time": time}


def load_sales_fact(src: pyodbc.Cursor, dwh: pyodbc.Cursor) -> None:
    """Befüllt Sales_Fact neu; fehlende Dimensionsschlüssel werden gezählt und geloggt."""
    keys = surrogate_key_maps(dwh)
    dwh.execute("DELETE FROM Sales_Fact")

    src.execute(
        "SELECT sh.CustomerID, sh.StoreID, sh.EmployeeID, sh.InvoiceDate, "
        "sd.ProductID, sd.Quantity, sd.UnitPrice "
        "FROM SalesHeaders sh JOIN SalesDetails sd ON sh.InvoiceNo = sd.InvoiceNo"
    )
    facts, skipped = [], Counter()
    for row in src.fetchall():
        lookup = {
            "product": keys["product"].get(row.ProductID),
            "customer": keys["customer"].get(row.CustomerID),
            "store": keys["store"].get(row.StoreID),
            "employee": keys["employee"].get(row.EmployeeID),
            "time": keys["time"].get((row.InvoiceDate.date(), row.InvoiceDate.hour)),
        }
        missing = [name for name, value in lookup.items() if value is None]
        if missing:
            skipped[", ".join(missing)] += 1
            continue
        facts.append((
            lookup["product"], lookup["customer"], lookup["store"], lookup["employee"],
            lookup["time"], row.Quantity, row.UnitPrice,
        ))

    dwh.executemany(
        "INSERT INTO Sales_Fact (Product_Dim_ID, Customer_Dim_ID, Store_Dim_ID, "
        "Employee_Dim_ID, Time_Dim_ID, Quantity, UnitPrice) VALUES (?, ?, ?, ?, ?, ?, ?)",
        facts,
    )
    logging.info("Sales_Fact: %s Zeilen geladen", f"{len(facts):,}")
    for reason, count in skipped.items():
        logging.warning("%s Zeilen übersprungen, fehlender Schlüssel: %s", count, reason)


def main() -> int:
    configure_logging()
    try:
        with connect(OLTP_DATABASE) as oltp, connect(DWH_DATABASE) as dwh_conn:
            src, dwh = oltp.cursor(), dwh_conn.cursor()
            load_static_dimensions(src, dwh)
            load_product_dimension_scd2(src, dwh)
            load_time_dimension(src, dwh)
            dwh_conn.commit()
            load_sales_fact(src, dwh)
            dwh_conn.commit()
    except (RuntimeError, pyodbc.Error) as error:
        logging.error("ETL abgebrochen: %s", error)
        return 1
    logging.info("ETL abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

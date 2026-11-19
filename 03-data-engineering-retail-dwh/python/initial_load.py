"""Initial Load: UCI-Online-Retail-CSV -> operative Datenbank Retail_OLTP.

Ablauf:
    1. CSV laden und Produkte regelbasiert kategorisieren
    2. Stammdaten (Countries, Categories, Products, Customers) idempotent einfügen
    3. Verkaufsbelege (SalesHeaders + SalesDetails) einfügen

Der Quelldatensatz kennt weder Filialen noch Mitarbeiter. Beide werden den
Belegen deshalb reproduzierbar zufällig (random.seed) zugeordnet, damit die
Dimensionen im DWH gefüllt sind.

Aufruf:  python python/initial_load.py [--max-rows 5000]
"""

import argparse
import logging
import random
import sys
from pathlib import Path

import pandas as pd
import pyodbc

from db_config import DATA_DIR, OLTP_DATABASE, configure_logging, connect

CSV_PATH = DATA_DIR / "data.csv"
CSV_ENCODING = "ISO-8859-1"

# Reihenfolge ist relevant: die erste passende Regel gewinnt.
CATEGORY_RULES = [
    ("Lighting", ("LIGHT", "CANDLE", "LANTERN")),
    ("Kitchenware", ("KITCHEN", "MUG", "PLATE", "BOWL")),
    ("Storage & Bags", ("BAG", "BOX", "STORAGE")),
    ("Gifts", ("HEART", "LOVE", "GIFT")),
]
DEFAULT_CATEGORY = "Home Decor"
MISSING_CATEGORY = "Others"
MAX_DESCRIPTION_LENGTH = 255


def categorize(description) -> str:
    """Ordnet eine Produktbeschreibung per Schlüsselwort einer Kategorie zu."""
    if pd.isna(description):
        return MISSING_CATEGORY
    text = str(description).upper()
    for category, keywords in CATEGORY_RULES:
        if any(keyword in text for keyword in keywords):
            return category
    return DEFAULT_CATEGORY


def to_price(value) -> float:
    """Wandelt einen Preis robust in float um; ungültige Werte werden 0.0."""
    try:
        price = round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if pd.isna(price) else price


def load_csv(path: Path) -> pd.DataFrame:
    """Liest die Online-Retail-Datei ein und ergänzt die Kategorie."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} fehlt. Download-Anleitung siehe data/README.md."
        )
    df = pd.read_csv(path, encoding=CSV_ENCODING)
    df["CategoryName"] = df["Description"].apply(categorize)
    logging.info("CSV geladen: %s Zeilen", f"{len(df):,}")
    return df


def upsert_lookup(cursor: pyodbc.Cursor, table: str, name_column: str,
                  id_column: str, values) -> dict:
    """Fügt fehlende Lookup-Werte ein und gibt {Name: ID} zurück."""
    cursor.executemany(
        f"IF NOT EXISTS (SELECT 1 FROM {table} WHERE {name_column} = ?) "
        f"INSERT INTO {table} ({name_column}) VALUES (?)",
        [(value, value) for value in values],
    )
    cursor.execute(f"SELECT {name_column}, {id_column} FROM {table}")
    return dict(cursor.fetchall())


def load_products(cursor: pyodbc.Cursor, df: pd.DataFrame, category_ids: dict) -> None:
    products = df[["StockCode", "Description", "CategoryName", "UnitPrice"]].drop_duplicates(
        "StockCode"
    )
    rows = [
        (
            str(row.StockCode),
            str(row.StockCode),
            (str(row.Description)[:MAX_DESCRIPTION_LENGTH]
             if pd.notna(row.Description) else "No Description"),
            category_ids[row.CategoryName],
            to_price(row.UnitPrice),
        )
        for row in products.itertuples(index=False)
    ]
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM Products WHERE StockCode = ?)
            INSERT INTO Products (StockCode, Description, CategoryID, CurrentPrice)
            VALUES (?, ?, ?, ?)
        """,
        rows,
    )
    logging.info("Produkte: %s verarbeitet", f"{len(rows):,}")


def load_customers(cursor: pyodbc.Cursor, df: pd.DataFrame, country_ids: dict) -> None:
    customers = df.dropna(subset=["CustomerID"]).drop_duplicates("CustomerID")
    fallback_country = next(iter(country_ids.values()))
    rows = [
        (int(row.CustomerID), int(row.CustomerID), country_ids.get(row.Country, fallback_country))
        for row in customers.itertuples(index=False)
    ]
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = ?)
            INSERT INTO Customers (CustomerID, CountryID) VALUES (?, ?)
        """,
        rows,
    )
    logging.info("Kunden: %s verarbeitet", f"{len(rows):,}")


def load_sales(cursor: pyodbc.Cursor, df: pd.DataFrame, max_rows: int) -> None:
    """Lädt Belegköpfe und Positionen für die ersten max_rows Verkaufszeilen."""
    cursor.execute("SELECT StockCode, ProductID FROM Products")
    product_ids = dict(cursor.fetchall())
    cursor.execute("SELECT StoreID FROM Stores")
    store_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT EmployeeID FROM Employees")
    employee_ids = [r[0] for r in cursor.fetchall()]
    if not store_ids or not employee_ids:
        raise RuntimeError("Stores/Employees sind leer. Zuerst sql/01_retail_oltp.sql ausführen.")

    sales = df.dropna(subset=["InvoiceNo", "CustomerID"]).head(max_rows).copy()
    sales["InvoiceNo"] = sales["InvoiceNo"].astype(str)
    sales["CustomerID"] = sales["CustomerID"].astype(int)

    random.seed(42)
    headers = sales.drop_duplicates("InvoiceNo")
    header_rows = [
        (
            row.InvoiceNo, row.InvoiceNo, row.InvoiceDate, row.CustomerID,
            random.choice(store_ids), random.choice(employee_ids),
        )
        for row in headers.itertuples(index=False)
    ]
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM SalesHeaders WHERE InvoiceNo = ?)
            INSERT INTO SalesHeaders (InvoiceNo, InvoiceDate, CustomerID, StoreID, EmployeeID)
            VALUES (?, ?, ?, ?, ?)
        """,
        header_rows,
    )

    detail_rows, unknown_products = [], 0
    for row in sales.itertuples(index=False):
        product_id = product_ids.get(str(row.StockCode))
        if product_id is None:
            unknown_products += 1
            continue
        detail_rows.append((row.InvoiceNo, product_id, int(row.Quantity), to_price(row.UnitPrice)))
    cursor.executemany(
        "INSERT INTO SalesDetails (InvoiceNo, ProductID, Quantity, UnitPrice) VALUES (?, ?, ?, ?)",
        detail_rows,
    )
    logging.info(
        "Verkäufe: %s Belege, %s Positionen, %s Positionen ohne Produkt übersprungen",
        f"{len(header_rows):,}", f"{len(detail_rows):,}", unknown_products,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=CSV_PATH, help="Pfad zur Online-Retail-CSV")
    parser.add_argument("--max-rows", type=int, default=5000, help="Anzahl Verkaufszeilen (Default 5000)")
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    try:
        df = load_csv(args.csv)
        with connect(OLTP_DATABASE) as conn:
            cursor = conn.cursor()
            country_ids = upsert_lookup(
                cursor, "Countries", "CountryName", "CountryID", df["Country"].dropna().unique()
            )
            category_ids = upsert_lookup(
                cursor, "Categories", "CategoryName", "CategoryID", df["CategoryName"].unique()
            )
            load_products(cursor, df, category_ids)
            load_customers(cursor, df, country_ids)
            conn.commit()
            load_sales(cursor, df, args.max_rows)
            conn.commit()
    except (FileNotFoundError, RuntimeError, pyodbc.Error) as error:
        logging.error("Initial Load abgebrochen: %s", error)
        return 1
    logging.info("OLTP-Datenbank erfolgreich befüllt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

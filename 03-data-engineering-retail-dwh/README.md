# Retail Data Warehouse (Data Engineering)

Operative Datenbank (OLTP) und Data Warehouse (Star Schema) für
Einzelhandelsdaten mit Python-ETL und analytischen Abfragen.
Modulprojekt Data Engineering.

## Architektur

```text
UCI Online Retail CSV
        │  python/initial_load.py  (Kategorisierung, Stammdaten, Belege)
        ▼
  Retail_OLTP (3NF, 8 Tabellen)
        │  python/etl_process.py   (Dimensionen, SCD 2, Zeit, Fakten)
        ▼
  Retail_DWH (Star Schema: 5 Dimensionen + Sales_Fact)
        │  sql/analytics/*.sql
        ▼
  Reports: Umsatztrend, Kategorien, Regionen, RFM-Segmente, Verkaufsstunden
```

Diagramme: [ER-Diagramm OLTP](docs/ER-Diagramm_Retail_OLTP.pdf),
[Star Schema DWH](docs/Star-Schema_Retail_DWH.pdf),
[Mapping-Tabelle OLTP → DWH](docs/Mapping-Tabelle_OLTP-DWH.ods),
[Speicherplatzschätzung](docs/Speicherplatzschaetzung.xlsx).

## Fachliche Besonderheiten

- **SCD Typ 2** in `Product_Dim`: Bei Preisänderung wird die alte Version mit
  `End_Date` geschlossen und eine neue aktive Version angelegt. Fakten zeigen
  dadurch immer auf den zum Verkaufszeitpunkt gültigen Preis.
- **Zeitdimension auf Stundenebene** (`FullDate`, `Hour` eindeutig), damit
  Tagesverlauf-Analysen möglich sind.
- **Berechnete, persistierte Spalte** `TotalPrice = Quantity × UnitPrice` in der
  Faktentabelle.
- **Idempotenter ETL**: Dimensionen werden nur ergänzt, die Faktentabelle wird
  pro Lauf neu aufgebaut. Surrogate Keys werden einmal in Dictionaries geladen
  statt pro Zeile abgefragt. Übersprungene Zeilen werden mit Grund geloggt.
- **Konfiguration über `.env`**: Servername und Treiber stehen nicht im Code.

## Ausführen

Voraussetzungen: SQL Server (Express reicht), ODBC Driver 17/18, Python 3.10+.

```bash
pip install -r requirements.txt
cp .env.example .env          # DB_SERVER eintragen
```

1. `sql/01_retail_oltp.sql` und `sql/02_retail_dwh.sql` in SSMS ausführen
   (legen beide Datenbanken samt Beispiel-Filialen und -Mitarbeitern an).
2. Quelldaten gemäß [data/README.md](data/README.md) als `data/data.csv` ablegen.
3. OLTP befüllen und DWH laden:

```bash
python python/initial_load.py --max-rows 5000
python python/etl_process.py
```

4. Analysen aus `sql/analytics/` in SSMS ausführen. Unter Windows startet
   `scripts/run_etl.bat` den ETL-Lauf, z. B. über die Aufgabenplanung.

## Struktur

```text
sql/01_retail_oltp.sql         OLTP-Schema + Stammdaten (Länder, Filialen, Mitarbeiter)
sql/02_retail_dwh.sql          Star Schema
sql/analytics/                 5 Analyseabfragen
python/db_config.py            Verbindung und Logging aus .env
python/initial_load.py         CSV -> OLTP
python/etl_process.py          OLTP -> DWH
scripts/run_etl.bat            Batch-Starter (Windows)
docs/                          Diagramme, Mapping, Speicherplatz, Agile-Tagesprotokolle
```

## Hinweise zum Datensatz

Der Online-Retail-Datensatz enthält weder Filialen noch Mitarbeiter. Beide
werden beim Initial Load reproduzierbar zufällig zugeordnet (`random.seed(42)`),
damit die Dimensionen des DWH befüllt und die Abfragen demonstrierbar sind.

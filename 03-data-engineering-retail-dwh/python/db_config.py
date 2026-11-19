"""Gemeinsame Datenbankkonfiguration für Initial Load und ETL.

Die Verbindungsdaten kommen aus Umgebungsvariablen bzw. einer `.env`-Datei
im Projektordner (Vorlage: `.env.example`). So landen keine Servernamen
oder Zugangsdaten im Code.
"""

import logging
import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"

load_dotenv(PROJECT_DIR / ".env")

OLTP_DATABASE = os.getenv("DB_OLTP", "Retail_OLTP")
DWH_DATABASE = os.getenv("DB_DWH", "Retail_DWH")


def configure_logging() -> None:
    """Einheitliches Log-Format für alle Skripte."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )


def connection_string(database: str) -> str:
    """Baut den ODBC-Connection-String aus den Umgebungsvariablen."""
    server = os.getenv("DB_SERVER")
    if not server:
        raise RuntimeError(
            "DB_SERVER ist nicht gesetzt. Bitte .env.example nach .env kopieren "
            "und den Servernamen eintragen."
        )
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    return (
        f"Driver={{{driver}}};Server={server};Database={database};"
        "Trusted_Connection=yes;"
    )


def connect(database: str) -> pyodbc.Connection:
    """Öffnet eine Verbindung und loggt das Ergebnis."""
    conn = pyodbc.connect(connection_string(database))
    logging.info("Verbunden mit %s", database)
    return conn

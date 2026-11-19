# Data & Analytics Portfolio – Mahsa Saeedzadeh

Fünf Modulprojekte aus meiner Weiterbildung zur Data Scientist / Data Engineer (2026).
Jedes Projekt deckt eine Stufe der Datenwertschöpfung ab: Datenmodellierung (SQL),
Programmierung (Python), Datenintegration (Data Engineering), explorative Analyse
(Data Analytics) und Modellierung (Machine Learning).

| # | Projekt | Thema | Technologien | Highlights |
|---|---|---|---|---|
| 01 | [CaféCRM](01-sql-cafe-crm/) | Datenmodellierung & T-SQL | MS SQL Server, T-SQL, MS Access, draw.io | 13 Tabellen, Stored Procedure mit Transaktion, Trigger, Rollen & Rechte, Seed-Daten, 8 Testskripte |
| 02 | [Sprachenspiel](02-python-sprachenspiel/) | Konsolenspiel | Python 3 (Standardbibliothek), unittest | OOP, Dateiverarbeitung, Eingabevalidierung, 4 Sprachen × 3 Stufen, Unit-Tests |
| 03 | [Retail Data Warehouse](03-data-engineering-retail-dwh/) | OLTP → Star Schema mit ETL | SQL Server, Python, pyodbc, pandas | 3NF-OLTP, Star Schema, SCD Typ 2, idempotenter Python-ETL, RFM-Analyse |
| 04 | [Human Activity Recognition](04-data-analytics-har/) | Sensordatenanalyse | Jupyter, pandas, scikit-learn, seaborn | Feature-Extraktion aus 1 800 Zeitreihen-Spalten, K-Means + PCA, Random Forest, Vergleich zweier Altersgruppen |
| 05 | [Wine Quality Prediction](05-machine-learning-wine-quality/) | Regressions-Benchmark | Python 3.12, scikit-learn, XGBoost | 14 Modelle in einer gemeinsamen Pipeline, GridSearchCV, abgesicherter einmaliger Holdout-Test |

Jedes Projekt hat ein eigenes README mit Aufbau, Ausführung und Erkenntnissen.

## Repository-Struktur

```text
.
├── 01-sql-cafe-crm/                  T-SQL-Skripte (DDL, Views, Funktionen, Procedure, Trigger,
│                                     Security, Seed), Tests, ER-Diagramm, Dokumentation, Access-Frontend
├── 02-python-sprachenspiel/          Spiel-Logik, Wortlisten, Unit-Tests, Screenshots
├── 03-data-engineering-retail-dwh/   DDL (OLTP + DWH), Python-ETL, Analyseabfragen, Diagramme
├── 04-data-analytics-har/            Jupyter-Notebook, Präsentation, Datenbeschreibung
├── 05-machine-learning-wine-quality/ Modell-Pipeline, Ergebnisberichte, eigenes README
├── .gitignore
├── LICENSE
└── README.md
```

Rohdaten sind **nicht** im Repository enthalten (Größe und Lizenz). Jedes Projekt
beschreibt in `data/README.md`, woher sie stammen und wo sie abzulegen sind.
Zugangsdaten und Servernamen liegen in `.env`-Dateien bzw. SQLCMD-Variablen,
nie im Code.

---

## 01 · CaféCRM – Relationale Datenbank (SQL)

**Aufgabe:** Entwurf und Implementierung eines CRM-Systems für ein Café mit
Kundenbindungsprogramm, Lagerverwaltung, Events und Mitarbeiter-Schulungen.

- ER-Modell → 13 normalisierte Tabellen mit PK/FK, Default- und Check-Constraints,
  Nonclustered Index; zwei n:m-Beziehungen
- 4 Views, 3 Funktionen (Treuepunkte, Rabattsatz, Lager-Warnung als
  Tabellenwertfunktion)
- Stored Procedure `usp_CreateNewOrder`: Bestandsprüfung mit Zeilensperre →
  Rabatt → Bestellung + Position → Treuepunkte, in einer Transaktion mit TRY/CATCH
- 2 DML-Trigger (Lagerreduktion, Mitarbeiter-KPI), mengenorientiert
- Login/User/Rolle nach Least-Privilege, Passwort als SQLCMD-Variable
- Seed-Skript mit konsistenten Testdaten, 8 Testskripte

**Technologien:** MS SQL Server 2022, T-SQL, SSMS, MS Access (ODBC), draw.io

**Ausführen:** Skripte in `sql/` in numerischer Reihenfolge (`001` → `060`),
dann `tests/`. Details im [Projekt-README](01-sql-cafe-crm/README.md).

> Teamprojekt (2 Personen). Datenmodell, Implementierung und Tests wurden
> gemeinsam erarbeitet.

---

## 02 · Sprachenspiel (Python)

**Aufgabe:** Wort-Ratespiel (Galgenmännchen-Prinzip) als Konsolenanwendung.

- Sprache (DE/EN/IT/ES) und Schwierigkeit (leicht/mittel/schwer) wählbar,
  Fehlversuche skalieren mit der Schwierigkeit
- Über 1 100 Wörter in 12 externen Textdateien, dynamisch geladen
- Klasse `Sprachenspiel` kapselt den Spielzustand; Ein-/Ausgabe getrennt
- Eingabevalidierung, `FileNotFoundError`/`ValueError` für fehlende oder leere Listen
- 8 Unit-Tests mit `unittest`

**Technologien:** Python 3.10+, nur Standardbibliothek

```bash
cd 02-python-sprachenspiel
python sprachenspiel.py
python -m unittest discover -s tests -v
```

---

## 03 · Retail Data Warehouse (Data Engineering)

**Aufgabe:** Operative Datenbank (OLTP) und Data Warehouse (Star Schema) für
Einzelhandelsdaten inklusive ETL-Strecke und Analysen.

- **OLTP (3NF):** 8 Tabellen (Länder, Kunden, Kategorien, Produkte, Filialen,
  Mitarbeiter, Belegkopf, Belegposition)
- **DWH (Star Schema):** 5 Dimensionen + Faktentabelle mit persistierter
  berechneter Spalte; Produktdimension als **SCD Typ 2**; Zeitdimension auf
  Stundenebene
- **Initial Load (Python):** UCI-Online-Retail-CSV, regelbasierte
  Produktkategorisierung, idempotente Stammdaten-Inserts, Belege
- **ETL (Python/pyodbc):** Dimensionen, SCD-2-Logik, Surrogate-Key-Lookups über
  Dictionaries, Faktentabelle; übersprungene Zeilen werden mit Grund geloggt
- **Analysen (T-SQL):** RFM-Kundensegmentierung, Umsatztrend, Kategorie-,
  Regional- und Stundenanalyse
- Konfiguration über `.env`, Logging, Batch-Starter für geplante Läufe

**Technologien:** MS SQL Server, T-SQL, Python 3, pandas, pyodbc, python-dotenv

```bash
cd 03-data-engineering-retail-dwh
pip install -r requirements.txt
cp .env.example .env              # Servername eintragen
# sql/01_retail_oltp.sql und sql/02_retail_dwh.sql in SSMS ausführen
python python/initial_load.py     # OLTP befüllen
python python/etl_process.py      # DWH laden
```

**Daten:** [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)
(CC BY 4.0), siehe `data/README.md`.

---

## 04 · Human Activity Recognition (Data Analytics)

**Aufgabe:** Analyse menschlicher Bewegungsmuster aus Smartphone- und
Wearable-Sensoren und Vergleich zweier Altersgruppen.

**Daten:** [KU-HAR](https://www.kaggle.com/datasets/niloy333/kuhar) (20 750
Zeitfenster × 1 803 Spalten, 18 Aktivitäten, 90 Probanden) und
[HAR70+](https://www.kaggle.com/datasets/anshtanwar/adult-subjects-70-95-years-activity-recognition)
(Rohdaten von Probanden ab 70 Jahren).

**Vorgehen & Erkenntnisse**

1. EDA: Struktur, Datentypen, Klassenverteilung, Label-Harmonisierung
2. Feature-Extraktion: 6 Sensorkanäle × (Mittelwert, Varianz, Standardabweichung,
   Energie) → 24 Features pro Sample; HAR70+ in 3-Sekunden-Fenster aggregiert
3. K-Means (k = 3) + PCA: ein dominantes Cluster, zwei Ausreißer-Cluster.
   Bewegungsintensität allein trennt die Aktivitäten nicht
4. Random Forest: 92 % Accuracy auf KU-HAR, 96 % auf HAR70+. Dort liegt der
   Macro-F1-Score aber nur bei 0,73, seltene Klassen sind also schwächer
5. Ältere Probanden zeigen deutlich geringere Bewegungsenergie und -varianz

**Technologien:** Jupyter, Python 3.12, pandas, NumPy, scikit-learn, matplotlib, seaborn

```bash
cd 04-data-analytics-har
pip install -r requirements.txt
# Daten gemäß data/README.md ablegen
jupyter notebook notebooks/har_analysis.ipynb
```

---

## 05 · Wine Quality Prediction (Machine Learning)

**Aufgabe:** Vorhersage der sensorischen Weinqualität (0–10) aus 11
physikochemischen Messwerten; fairer Vergleich vieler Regressionsmodelle.

- Gemeinsame Pipeline für 14 Modelle (Baseline bis Voting/Stacking)
- Reproduzierbarer Split: Duplikate entfernt, qualitäts-stratifiziert und
  feature-ranked, Ausreißer nur im Training entfernt (3 × IQR)
- 5-fache Kreuzvalidierung (MAE, RMSE, R²) plus klassifikationsähnliche Sicht
- Optionale `GridSearchCV` je Modell ohne Zugriff auf den Holdout
- **Abgesicherter einmaliger Holdout-Test:** Konfiguration per SHA-256-Lock
  eingefroren, danach genau einmal auf den 20 %-Testdaten bewertet
- Ergebnisberichte: Experiment-Register, Grid-Search-Report, finaler Testreport

**Technologien:** Python 3.12, NumPy, pandas, scikit-learn, XGBoost

```bash
cd 05-machine-learning-wine-quality
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py --wine both --model all
```

**Daten:** [UCI Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality)
(CC BY 4.0), liegt unter `data/raw-input/`. Details im
[Projekt-README](05-machine-learning-wine-quality/README.md).

> Teamprojekt: Die Modellfamilien wurden in Kleingruppen beigesteuert und in
> eine gemeinsame Pipeline integriert.

---

## Kontakt

Mahsa Saeedzadeh · [GitHub](https://github.com/Mahsa-Saeedzadeh)

## Lizenz

Code unter [MIT-Lizenz](LICENSE). Die verwendeten Datensätze unterliegen den
Lizenzen der jeweiligen Anbieter (UCI, Kaggle).

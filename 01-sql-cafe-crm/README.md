# CaféCRM – Relationale Datenbank (MS SQL Server)

CRM- und Warenwirtschaftsdatenbank für ein Café mit Kundenbindungsprogramm,
Lagerverwaltung, Events und Mitarbeiter-Schulungen. Modulprojekt SQL
(Teamprojekt, 2 Personen).

## Datenmodell

13 Tabellen in 3. Normalform, zwei n:m-Beziehungen (Kunde ↔ Event,
Mitarbeiter ↔ Training). ER-Diagramm: [docs/ER-Diagramm.pdf](docs/ER-Diagramm.pdf),
fachliches Konzept: [docs/CafeCRM-Konzept.pdf](docs/CafeCRM-Konzept.pdf),
ausführliche Dokumentation: [docs/Dokumentation.pdf](docs/Dokumentation.pdf).

| Bereich | Tabellen |
|---|---|
| Verkauf | `Order`, `OrderItem`, `Product`, `ProductCategory` |
| Lager | `Inventory`, `Supplier` |
| Kunden | `Customer`, `LoyaltyLevel`, `CafeEvent`, `CustomerEvent` |
| Personal | `Employee`, `EmployeeKPI`, `Training`, `EmployeeTraining` |

## Datenbankobjekte

| Datei | Objekt | Zweck |
|---|---|---|
| `sql/001_create_database.sql` | DDL | Datenbank, Tabellen, PK/FK, Check- und Default-Constraints, Index |
| `sql/010–013_view_*.sql` | 4 Views | Verkaufsübersicht, Bestelldetails, Umsatz pro Mitarbeiter (GROUP BY/HAVING), inaktive Kunden (LEFT JOIN) |
| `sql/020–022_function_*.sql` | 3 Funktionen | Treuepunkte, Rabattsatz nach Loyalty-Level, Tabellenwertfunktion Lager-Warnung |
| `sql/030_procedure_CreateNewOrder.sql` | Stored Procedure | Bestellung anlegen: Bestandsprüfung, Rabatt, Position, Treuepunkte in einer Transaktion mit TRY/CATCH |
| `sql/040–041_trigger_*.sql` | 2 Trigger | Lagerbestand nach Verkauf reduzieren, KPI-Score des Mitarbeiters erhöhen |
| `sql/050_security_login_user_role.sql` | Login/User | Anwendungsbenutzer mit Lese-/Schreibrechten (Least Privilege) |
| `sql/060_seed_data.sql` | Testdaten | Fiktive, konsistente Daten für alle Tabellen |
| `tests/test_01–08_*.sql` | Tests | Basisdaten, Transaktionslogik, n:m, Views, Constraints, Berechtigungen, Skalarfunktion, referenzielle Integrität |

## Ausführen

Voraussetzung: SQL Server 2016 oder neuer (wegen `CREATE OR ALTER`), SSMS.

1. `sql/001_create_database.sql` ausführen.
2. Objekt-Skripte `010` bis `041` in numerischer Reihenfolge ausführen.
3. `050_security_login_user_role.sql` im **SQLCMD-Modus** ausführen und vorher
   das Passwort setzen (`:setvar AppPassword "..."`). Das Passwort steht
   bewusst nicht im Repository.
4. `060_seed_data.sql` ausführen.
5. Tests aus `tests/` einzeln ausführen; jeder Test dokumentiert im Kopf das
   erwartete Ergebnis. Test 8 läuft in einer Transaktion mit Rollback.

Alternativ per Kommandozeile:

```bash
for f in sql/*.sql; do sqlcmd -S localhost -E -i "$f" -v AppPassword="<Passwort>"; done
```

## Frontend und Datenimport

- `frontend/CafeCRM_Frontend.accdb`: MS-Access-Oberfläche, angebunden über
  eine ODBC-DSN `CafeCrmSystem` mit Windows-Authentifizierung.
- `data/products.csv` plus Screenshots in `docs/import-screenshots/`
  dokumentieren den Import der Produktliste über den SQL-Server-Import-Assistenten.

## Gelernt

- Geschäftslogik gehört in eine Transaktion: Bestandsprüfung mit
  `UPDLOCK, HOLDLOCK`, damit parallele Bestellungen nicht überbuchen.
- Trigger müssen mengenorientiert sein (`inserted` kann mehrere Zeilen
  enthalten) und Constraints wie `CHECK (Score BETWEEN 0 AND 100)` respektieren.
- Zugangsdaten gehören nie ins Skript, sondern in SQLCMD-Variablen oder
  einen Secret Store.

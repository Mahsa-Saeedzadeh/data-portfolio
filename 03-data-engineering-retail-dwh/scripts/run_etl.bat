@echo off
:: Startet den ETL-Lauf OLTP -> DWH. Pfade sind relativ zum Projektordner,
:: damit das Skript auf jedem Rechner (z. B. per Windows-Aufgabenplanung) läuft.
cd /d "%~dp0.."
echo Starte ETL-Prozess...
python python\etl_process.py
if errorlevel 1 (
    echo ETL fehlgeschlagen, siehe Log oben.
) else (
    echo ETL-Prozess abgeschlossen.
)
pause

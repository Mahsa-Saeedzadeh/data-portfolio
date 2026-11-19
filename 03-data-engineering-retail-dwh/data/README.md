# Daten

Der Quelldatensatz ist nicht im Repository enthalten.

1. **UCI Online Retail** herunterladen:
   <https://archive.ics.uci.edu/dataset/352/online+retail> (Lizenz CC BY 4.0,
   ca. 540 000 Transaktionen eines britischen Online-Händlers, Dez. 2010 bis Dez. 2011).
2. Die Excel-Datei als CSV exportieren und hier als `data.csv` ablegen.
   Erwartete Spalten: `InvoiceNo, StockCode, Description, Quantity, InvoiceDate,
   UnitPrice, CustomerID, Country`. Encoding: ISO-8859-1.
3. `python python/initial_load.py` lädt standardmäßig die ersten 5 000
   Verkaufszeilen; mit `--max-rows` lässt sich das anpassen.

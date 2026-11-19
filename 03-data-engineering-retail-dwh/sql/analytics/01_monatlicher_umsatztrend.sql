/* Monatlicher Umsatz und Transaktionsanzahl (Trendanalyse)
   Datenbank: Retail_DWH */
USE Retail_DWH;
GO

SELECT
    t.Year AS Jahr,
    t.Month AS Monat,
    FORMAT(SUM(f.TotalPrice), 'N0') AS Monatsumsatz,
    COUNT(f.Sales_Fact_ID) AS Anzahl_Transaktionen
FROM Sales_Fact f
JOIN Time_Dim t ON f.Time_Dim_ID = t.Time_Dim_ID
GROUP BY t.Year, t.Month
ORDER BY t.Year, t.Month;

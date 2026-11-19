/* Verkäufe und Umsatz je Tagesstunde (nutzt Time_Dim.Hour)
   Datenbank: Retail_DWH */
USE Retail_DWH;
GO

SELECT
    t.Hour AS Stunde,
    COUNT(f.Sales_Fact_ID) AS Verkaufsanzahl,
    FORMAT(SUM(f.TotalPrice), 'N0') AS Umsatz_Pro_Stunde
FROM Sales_Fact f
JOIN Time_Dim t ON f.Time_Dim_ID = t.Time_Dim_ID
GROUP BY t.Hour
ORDER BY t.Hour;

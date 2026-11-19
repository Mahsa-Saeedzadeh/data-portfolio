/* Umsatz je Land und Filiale
   Datenbank: Retail_DWH */
USE Retail_DWH;
GO

SELECT
    s.CountryName AS Land,
    s.StoreName AS Filiale,
    FORMAT(SUM(f.TotalPrice), 'N0') AS Filialumsatz
FROM Sales_Fact f
JOIN Store_Dim s ON f.Store_Dim_ID = s.Store_Dim_ID
GROUP BY s.CountryName, s.StoreName
ORDER BY SUM(f.TotalPrice) DESC;

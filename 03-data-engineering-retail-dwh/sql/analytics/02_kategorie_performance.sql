/* Verkaufte Einheiten und Umsatz je Produktkategorie
   Datenbank: Retail_DWH */
USE Retail_DWH;
GO

SELECT
    p.CategoryName AS Kategorie,
    SUM(f.Quantity) AS Verkaufte_Einheiten,
    FORMAT(SUM(f.TotalPrice), 'N0') AS Gesamtumsatz
FROM Sales_Fact f
JOIN Product_Dim p ON f.Product_Dim_ID = p.Product_Dim_ID
GROUP BY p.CategoryName
ORDER BY SUM(f.TotalPrice) DESC;

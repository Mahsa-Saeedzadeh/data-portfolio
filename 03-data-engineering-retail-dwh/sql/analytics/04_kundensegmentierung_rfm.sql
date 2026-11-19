/* RFM-Kundensegmentierung (Recency, Frequency, Monetary)
   Datenbank: Retail_DWH */
USE Retail_DWH;
GO

WITH CustomerRFM AS (
    SELECT
        c.CustomerID,
        DATEDIFF(DAY, MAX(t.FullDate), GETDATE()) AS Recency,
        COUNT(f.Sales_Fact_ID) AS Frequency,
        SUM(f.TotalPrice) AS MonetaryValue
    FROM Sales_Fact f
    JOIN Customer_Dim c ON f.Customer_Dim_ID = c.Customer_Dim_ID
    JOIN Time_Dim t ON f.Time_Dim_ID = t.Time_Dim_ID
    GROUP BY c.CustomerID
)
SELECT
    CustomerID,
    Recency AS Tage_Seit_Letztem_Kauf,
    Frequency AS Kaufhaeufigkeit,
    MonetaryValue AS Gesamtwert,
    CASE
        WHEN Recency < 30 AND Frequency > 5 THEN 'A-Kunde (Aktiv)'
        WHEN Recency > 180 THEN 'Inaktivitätsrisiko'
        WHEN MonetaryValue > 2000 THEN 'Premium-Kunde'
        ELSE 'Standard'
    END AS Kunden_Segment
FROM CustomerRFM;

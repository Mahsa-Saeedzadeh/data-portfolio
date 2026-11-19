USE CafeCRM_DB;
GO

/* ============================================================
   View: vw_InactiveClients
   Beschreibung:
   Zeigt alle Kunden, die noch keine Bestellung aufgegeben haben.
   ============================================================ */

CREATE OR ALTER VIEW dbo.vw_InactiveClients AS
SELECT 
    C.CustomerID,
    C.FirstName,
    C.LastName
FROM dbo.Customer C
LEFT JOIN dbo.[Order] O 
    ON C.CustomerID = O.CustomerID
WHERE O.OrderID IS NULL;
GO

/* ============================================================
   Trigger: trg_UpdateEmployeeKPI
   Beschreibung:
   Erhöht den KPI-Score des bearbeitenden Mitarbeiters um 1 pro
   neuer Bestellung. Der Score ist durch CHK_KPI_Score auf 0–100
   begrenzt, deshalb wird bei 100 gedeckelt. Mengenoperationen
   (mehrere Zeilen in 'inserted') werden korrekt aggregiert.
   ============================================================ */

USE CafeCRM_DB;
GO

CREATE OR ALTER TRIGGER dbo.trg_UpdateEmployeeKPI
ON dbo.[Order]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE k
    SET Score = CASE
                    WHEN ISNULL(k.Score, 0) + n.NewOrders > 100 THEN 100
                    ELSE ISNULL(k.Score, 0) + n.NewOrders
                END
    FROM dbo.EmployeeKPI AS k
    INNER JOIN (
        SELECT EmployeeID, COUNT(*) AS NewOrders
        FROM inserted
        WHERE EmployeeID IS NOT NULL
        GROUP BY EmployeeID
    ) AS n ON n.EmployeeID = k.EmployeeID;
END;
GO

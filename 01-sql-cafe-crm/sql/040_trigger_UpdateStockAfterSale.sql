USE CafeCRM_DB;
GO

/* ============================================================
   Trigger: trg_UpdateStockAfterSale
   Beschreibung:
   Reduziert automatisch den Lagerbestand nach jedem Verkauf.
   Wird ausgelöst, wenn ein neuer OrderItem-Datensatz eingefügt wird.
   Ein negativer Bestand wird durch CHK_InventoryQty verhindert; die
   auslösende Bestellung schlägt dann fehl.
   ============================================================ */

CREATE OR ALTER TRIGGER dbo.trg_UpdateStockAfterSale
ON dbo.OrderItem
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Inv
    SET Inv.QuantityInStock = Inv.QuantityInStock - Ins.Quantity
    FROM Inventory Inv
    INNER JOIN inserted Ins 
        ON Inv.ProductID = Ins.ProductID;
END;
GO

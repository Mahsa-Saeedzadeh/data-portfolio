/* ============================================================
   Stored Procedure: usp_CreateNewOrder
   Beschreibung:
   Legt eine Bestellung mit einer Position an und führt die
   komplette Geschäftslogik in einer Transaktion aus:
     1. Bestandsprüfung (mit Zeilensperre gegen Überbuchung)
     2. Produktpreis ermitteln
     3. Rabatt nach Loyalty-Level (fn_GetDiscountRate)
     4. Bestellung + Position anlegen
        (trg_UpdateStockAfterSale reduziert den Lagerbestand)
     5. Treuepunkte gutschreiben (fn_CalcLoyaltyPoints)
   Rückgabe: 0 = Erfolg, 1 = fachlicher oder technischer Fehler,
             Details in @ResultMsg.
   ============================================================ */

USE CafeCRM_DB;
GO

CREATE OR ALTER PROCEDURE dbo.usp_CreateNewOrder
    @CustomerID INT,
    @EmployeeID INT,
    @ProductID  INT,
    @Quantity   INT,
    @ResultMsg  NVARCHAR(200) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE
        @UnitPrice  DECIMAL(10,2),
        @Discount   DECIMAL(5,2),
        @FinalPrice DECIMAL(12,2),
        @OrderID    INT;

    IF @Quantity IS NULL OR @Quantity <= 0
    BEGIN
        SET @ResultMsg = N'Abbruch: Menge muss größer als 0 sein.';
        RETURN 1;
    END;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. Bestandsprüfung
        IF NOT EXISTS (
            SELECT 1
            FROM dbo.Inventory WITH (UPDLOCK, HOLDLOCK)
            WHERE ProductID = @ProductID AND QuantityInStock >= @Quantity
        )
        BEGIN
            ROLLBACK TRANSACTION;
            SET @ResultMsg = N'Abbruch: Lagerbestand nicht ausreichend.';
            RETURN 1;
        END;

        -- 2. Produktpreis
        SELECT @UnitPrice = Price
        FROM dbo.Product
        WHERE ProductID = @ProductID AND IsActive = 1;

        IF @UnitPrice IS NULL
        BEGIN
            ROLLBACK TRANSACTION;
            SET @ResultMsg = N'Abbruch: Produkt nicht gefunden oder inaktiv.';
            RETURN 1;
        END;

        -- 3. Rabatt
        SET @Discount   = dbo.fn_GetDiscountRate(@CustomerID);
        SET @FinalPrice = (@UnitPrice * @Quantity) * (1 - @Discount / 100);

        -- 4. Bestellung + Position
        INSERT INTO dbo.[Order] (CustomerID, EmployeeID, TotalAmount, FinalAmount)
        VALUES (@CustomerID, @EmployeeID, @UnitPrice * @Quantity, @FinalPrice);

        SET @OrderID = SCOPE_IDENTITY();

        INSERT INTO dbo.OrderItem (OrderID, ProductID, Quantity, UnitPrice)
        VALUES (@OrderID, @ProductID, @Quantity, @UnitPrice);

        -- 5. Treuepunkte
        UPDATE dbo.Customer
        SET TotalPoints = TotalPoints + dbo.fn_CalcLoyaltyPoints(@FinalPrice)
        WHERE CustomerID = @CustomerID;

        COMMIT TRANSACTION;

        SET @ResultMsg = CONCAT(N'Erfolg: Bestellung ', @OrderID,
                                N' angelegt, Endbetrag ', @FinalPrice, N' EUR.');
        RETURN 0;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        SET @ResultMsg = CONCAT(N'Fehler: ', ERROR_MESSAGE());
        RETURN 1;
    END CATCH;
END;
GO

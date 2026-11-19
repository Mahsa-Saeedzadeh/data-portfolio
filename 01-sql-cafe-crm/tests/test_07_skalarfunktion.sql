USE CafeCRM_DB;
GO

/* TEST 8: Skalarfunktion 'fn_GetDiscountRate'
   Ziel: Prüfung, ob ein VIP-Kunde den korrekten Rabattsatz erhält.
*/

DECLARE @Discount DECIMAL(5,2);
-- Kunde 11 ist laut Seed-Daten Platin-Kunde (15 % Rabatt)
SET @Discount = dbo.fn_GetDiscountRate(11);

PRINT 'Der Rabattsatz für diesen Kunden beträgt: ' + CAST(@Discount AS NVARCHAR) + '%';
-- Erwartung: 15.00%
GO

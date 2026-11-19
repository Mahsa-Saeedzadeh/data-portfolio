/* ============================================================
   Login & User Setup für CafeCRM_DB
   Beschreibung:
   Erstellt einen eingeschränkten Anwendungsbenutzer, der nur
   Daten lesen und schreiben darf (Least Privilege). Das Passwort
   steht nicht im Skript, sondern wird als SQLCMD-Variable
   übergeben:

     * SSMS:   Menü "Abfrage" > "SQLCMD-Modus" aktivieren und die
               :setvar-Zeile unten anpassen.
     * sqlcmd: sqlcmd -S <Server> -i 050_security_login_user_role.sql
                      -v AppPassword="<starkes Passwort>"
   ============================================================ */

:on error exit
:setvar AppPassword "BITTE_SETZEN"

USE master;
GO

IF '$(AppPassword)' = 'BITTE_SETZEN'
    RAISERROR ('Bitte AppPassword per :setvar oder -v setzen.', 16, 1);
GO

-- Login erstellen (falls nicht vorhanden)
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'CafeAppUser')
BEGIN
    CREATE LOGIN CafeAppUser
    WITH PASSWORD = N'$(AppPassword)',
         CHECK_POLICY = ON,
         CHECK_EXPIRATION = OFF;
END;
GO

USE CafeCRM_DB;
GO

-- Datenbankbenutzer neu anlegen (Synchronisation mit dem Login sicherstellen)
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'CafeAppUser')
    DROP USER CafeAppUser;
GO

CREATE USER CafeAppUser FOR LOGIN CafeAppUser;
GO

-- Berechtigungen vergeben (Least Privilege)
ALTER ROLE db_datareader ADD MEMBER CafeAppUser;
ALTER ROLE db_datawriter ADD MEMBER CafeAppUser;
GRANT EXECUTE ON dbo.usp_CreateNewOrder TO CafeAppUser;
GO

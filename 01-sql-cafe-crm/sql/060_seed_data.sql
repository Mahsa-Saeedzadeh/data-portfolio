/* ============================================================
   Seed-Daten für CafeCRM_DB
   Beschreibung:
   Fügt konsistente, rein fiktive Testdaten in alle 13 Tabellen
   ein. Nach den Objekt-Skripten (010–050) ausführen, damit die
   Trigger beim Einfügen der Bestellpositionen den Lagerbestand
   bereits mitführen. Alle Namen, E-Mails und Telefonnummern
   sind erfunden (example.com, 0000-Nummern).
   Voraussetzung: frische Datenbank (IDENTITY-Werte starten bei 1).
   ============================================================ */

USE CafeCRM_DB;
GO

SET NOCOUNT ON;
BEGIN TRANSACTION;

---------------------------------------------------------------
-- Stammdaten
---------------------------------------------------------------
INSERT INTO dbo.LoyaltyLevel (LevelName, MinPoints, DiscountPercent) VALUES
('Bronze',   0,  0.00),
('Silber', 100,  5.00),
('Gold',   300, 10.00),
('Platin', 600, 15.00);

INSERT INTO dbo.ProductCategory (CategoryName) VALUES
('Kaffee'), ('Tee'), ('Kaltgetränke'), ('Gebäck'), ('Merchandise'), ('Eis');

-- Produkte entsprechend data/products.csv (Preise in EUR)
INSERT INTO dbo.Product (ProductName, CategoryID, Price, IsActive) VALUES
(N'Saffron Latte (Persian Style)',      1, 5.50, 1),
(N'Matcha Green Tea Latte',             2, 5.90, 1),
(N'Persian Black Tea (Lahijan)',        2, 3.50, 1),
(N'Sencha Japanese Green Tea',          2, 4.20, 1),
(N'Cardamom Coffee (Turkish Style)',    1, 4.80, 1),
(N'Iced Mochi Coffee',                  1, 6.20, 1),
(N'Rosewater Lemonade (Sekanjabin)',    3, 4.50, 1),
(N'Yuzu Citrus Soda',                   3, 4.90, 1),
(N'Baklava Selection (Tehran)',         4, 7.50, 1),
(N'Matcha Cheesecake',                  4, 6.80, 1),
(N'Date & Walnut Cake',                 4, 5.20, 1),
(N'Dorayaki (Red Bean Pancake)',        4, 4.50, 1),
(N'Saffron Ice Cream (Bastani)',        6, 5.50, 1),
(N'Black Sesame Ice Cream',             6, 5.50, 1),
(N'Espresso (Tokyo Roast)',             1, 2.80, 1),
(N'Tasse mit dem Logo',                 5, 9.50, 1);

INSERT INTO dbo.Supplier (SupplierName, ContactEmail, Phone, City, Street, ZipCode) VALUES
(N'Rösterei Nord',     'info@roesterei-nord.example.com', '+49 40 0000001', 'Hamburg', 'Hafenstr. 1',   '20457'),
(N'Teehaus Sakura',    'order@sakura-tea.example.com',    '+49 30 0000002', 'Berlin',  'Teeweg 12',     '10115'),
(N'Patisserie Darya',  'hello@darya.example.com',         '+49 89 0000003', 'München', 'Backgasse 3',   '80331');

-- Lagerbestand: Produkte 9 und 12 liegen bewusst unter dem Mindestbestand (fn_InventoryAlert)
INSERT INTO dbo.Inventory (ProductID, QuantityInStock, MinimumStock, SupplierID) VALUES
( 1, 120, 10, 1), ( 2,  80, 10, 2), ( 3,  95, 10, 2), ( 4,  60, 10, 2),
( 5,  70, 10, 1), ( 6,  45, 10, 1), ( 7,  50, 10, 3), ( 8,  40, 10, 3),
( 9,   4, 10, 3), (10,  25, 10, 3), (11,  30, 10, 3), (12,   6, 10, 3),
(13,  35, 10, 3), (14,  35, 10, 3), (15, 200, 20, 1), (16,  18,  5, NULL);

INSERT INTO dbo.Employee (FirstName, LastName, Position, HireDate, Salary, Phone, City, Street, ZipCode) VALUES
(N'Lena',   N'Berger',   N'Filialleitung',  '2022-03-01', 3400.00, '0170 0000001', 'Berlin', 'Kaffeestr. 1',  '10115'),
(N'Omid',   N'Rahimi',   N'Barista',        '2023-01-15', 2600.00, '0170 0000002', 'Berlin', 'Bohnenweg 4',   '10117'),
(N'Yuki',   N'Tanaka',   N'Barista',        '2023-06-01', 2600.00, '0170 0000003', 'Berlin', 'Teeallee 8',    '10119'),
(N'Sara',   N'Kowalski', N'Service',        '2024-02-10', 2300.00, '0170 0000004', 'Berlin', 'Zuckergasse 2', '10178'),
(N'Daniel', N'Fuchs',    N'Konditor',       '2021-09-01', 2900.00, '0170 0000005', 'Berlin', 'Mehlstr. 7',    '10179'),
(N'Nina',   N'Hoffmann', N'Aushilfe',       '2025-04-01', 1500.00, '0170 0000006', 'Berlin', 'Milchweg 3',    '10243');

-- Kunden: 1 = Bronze, 11 = Platin (15 %), 10 und 12 ohne Bestellung (vw_InactiveClients)
INSERT INTO dbo.Customer (FirstName, LastName, Email, Phone, RegistrationDate, TotalPoints, LoyaltyLevelID) VALUES
(N'Anna',    N'Schmidt',  'anna.schmidt@example.com',    '0151 0000001', '2025-01-10',   0, 1),
(N'Reza',    N'Karimi',   'reza.karimi@example.com',     '0151 0000002', '2025-01-12', 120, 2),
(N'Mei',     N'Lin',      'mei.lin@example.com',         '0151 0000003', '2025-02-01',  45, 1),
(N'Jonas',   N'Weber',    'jonas.weber@example.com',     '0151 0000004', '2025-02-15', 310, 3),
(N'Fatima',  N'Nouri',    'fatima.nouri@example.com',    '0151 0000005', '2025-03-03',  20, 1),
(N'Lukas',   N'Meyer',    'lukas.meyer@example.com',     '0151 0000006', '2025-03-20', 150, 2),
(N'Aiko',    N'Sato',     'aiko.sato@example.com',       '0151 0000007', '2025-04-05',  80, 1),
(N'Tom',     N'Becker',   'tom.becker@example.com',      '0151 0000008', '2025-04-22', 400, 3),
(N'Leila',   N'Ahmadi',   'leila.ahmadi@example.com',    '0151 0000009', '2025-05-01',  10, 1),
(N'Paul',    N'Krüger',   'paul.krueger@example.com',    '0151 0000010', '2025-05-18',   0, 1),
(N'Shirin',  N'Zand',     'shirin.zand@example.com',     '0151 0000011', '2024-11-02', 720, 4),
(N'Hana',    N'Kimura',   'hana.kimura@example.com',     '0151 0000012', '2025-06-01',   0, 1);

---------------------------------------------------------------
-- Events, Trainings, KPIs (n:m-Beziehungen)
---------------------------------------------------------------
INSERT INTO dbo.CafeEvent (EventName, EventDate, Location) VALUES
(N'Persische Teezeremonie',       '2025-03-15', N'Café, Hauptraum'),
(N'Matcha-Workshop',              '2025-05-10', N'Café, Werkstatt'),
(N'Latte-Art Abend',              '2025-06-21', N'Café, Bar');

INSERT INTO dbo.CustomerEvent (CustomerID, EventID) VALUES
(1, 1), (2, 1), (4, 1), (3, 2), (6, 2), (11, 2), (8, 3), (11, 3);

INSERT INTO dbo.Training (TrainingName, TrainingDate) VALUES
(N'SCA Barista Skills Foundation',   '2024-10-05'),
(N'SCA Brewing Intermediate',        '2025-02-20'),
(N'Hygieneschulung HACCP',           '2025-01-08');

INSERT INTO dbo.EmployeeTraining (EmployeeID, TrainingID) VALUES
(1, 1), (1, 2), (2, 1), (3, 1), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3);

INSERT INTO dbo.EmployeeKPI (EmployeeID, SalesAmount, EvaluationDate, Score) VALUES
(1, 4200.00, '2025-06-30', 85),
(2, 3100.00, '2025-06-30', 72),
(3, 2950.00, '2025-06-30', 70),
(4, 1800.00, '2025-06-30', 60),
(5, 2200.00, '2025-06-30', 65),
(6,  600.00, '2025-06-30', 50);

---------------------------------------------------------------
-- Bestellungen (die Trigger aktualisieren Lager und KPI-Score)
---------------------------------------------------------------
INSERT INTO dbo.[Order] (CustomerID, EmployeeID, OrderDate, TotalAmount, FinalAmount, PaymentMethod) VALUES
( 1, 2, '2025-06-01 08:15', 11.00, 11.00, N'Karte'),
( 2, 2, '2025-06-01 09:40', 15.00, 14.25, N'Bar'),
( 4, 3, '2025-06-02 10:05', 12.30, 11.07, N'Karte'),
( 6, 3, '2025-06-02 14:20',  9.80,  9.31, N'Karte'),
( 8, 2, '2025-06-03 11:30', 22.50, 20.25, N'App'),
(11, 1, '2025-06-03 16:45', 28.00, 23.80, N'Karte'),
( 3, 4, '2025-06-04 08:50',  4.50,  4.50, N'Bar'),
( 5, 4, '2025-06-04 12:10', 10.90, 10.90, N'Karte'),
( 7, 3, '2025-06-05 15:00',  6.80,  6.80, N'App'),
( 9, 2, '2025-06-05 17:25',  5.50,  5.50, N'Bar'),
(11, 1, '2025-06-06 09:00', 19.00, 16.15, N'Karte'),
( 2, 3, '2025-06-06 13:35',  8.70,  8.27, N'Bar');

INSERT INTO dbo.OrderItem (OrderID, ProductID, Quantity, UnitPrice) VALUES
( 1,  1, 2, 5.50),
( 2,  6, 1, 6.20), ( 2,  9, 1, 7.50),  -- Summe 13.70, Rest Trinkgeld
( 3,  2, 1, 5.90), ( 3, 12, 1, 4.50),
( 4,  3, 1, 3.50), ( 4, 13, 1, 5.50),
( 5,  9, 3, 7.50),
( 6, 16, 2, 9.50), ( 6, 10, 1, 6.80),
( 7,  7, 1, 4.50),
( 8,  5, 1, 4.80), ( 8, 11, 1, 5.20),
( 9, 10, 1, 6.80),
(10, 14, 1, 5.50),
(11,  1, 2, 5.50), (11,  9, 1, 7.50),
(12,  4, 1, 4.20), (12, 15, 1, 2.80);

COMMIT TRANSACTION;

SELECT 'LoyaltyLevel' AS Tabelle, COUNT(*) AS Zeilen FROM dbo.LoyaltyLevel
UNION ALL SELECT 'ProductCategory', COUNT(*) FROM dbo.ProductCategory
UNION ALL SELECT 'Product',         COUNT(*) FROM dbo.Product
UNION ALL SELECT 'Supplier',        COUNT(*) FROM dbo.Supplier
UNION ALL SELECT 'Inventory',       COUNT(*) FROM dbo.Inventory
UNION ALL SELECT 'Employee',        COUNT(*) FROM dbo.Employee
UNION ALL SELECT 'Customer',        COUNT(*) FROM dbo.Customer
UNION ALL SELECT 'CafeEvent',       COUNT(*) FROM dbo.CafeEvent
UNION ALL SELECT 'CustomerEvent',   COUNT(*) FROM dbo.CustomerEvent
UNION ALL SELECT 'Training',        COUNT(*) FROM dbo.Training
UNION ALL SELECT 'EmployeeTraining',COUNT(*) FROM dbo.EmployeeTraining
UNION ALL SELECT 'EmployeeKPI',     COUNT(*) FROM dbo.EmployeeKPI
UNION ALL SELECT 'Order',           COUNT(*) FROM dbo.[Order]
UNION ALL SELECT 'OrderItem',       COUNT(*) FROM dbo.OrderItem;
GO

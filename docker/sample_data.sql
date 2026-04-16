-- Sample data for Store Management System
-- Usage:
--   docker exec <container> python -c "
--     import sqlite3; db = sqlite3.connect('data/store.db');
--     db.executescript(open('docker/sample_data.sql').read()); db.close()
--   "
-- Or locally: sqlite3 data/store.db < docker/sample_data.sql

-- Products (consumer goods / FMCG distribution)
INSERT INTO Product (PID, PName, Unit1, Unit2, ConversionFactor, Quantity, Price) VALUES
('P001', 'Nước mắm Chinsu 500ml', 'Thùng', 'Chai', 12, 50, 360000),
('P002', 'Dầu ăn Tường An 1L', 'Thùng', 'Chai', 12, 40, 540000),
('P003', 'Mì Hảo Hảo tôm chua cay', 'Thùng', 'Gói', 30, 100, 105000),
('P004', 'Sữa Vinamilk 220ml', 'Thùng', 'Hộp', 48, 80, 336000),
('P005', 'Bột giặt Omo 3kg', 'Thùng', 'Bịch', 4, 30, 320000),
('P006', 'Nước ngọt Coca Cola 330ml', 'Thùng', 'Lon', 24, 60, 216000),
('P007', 'Đường Biên Hòa 1kg', 'Bao', NULL, NULL, 200, 22000),
('P008', 'Gạo ST25 5kg', 'Bao', NULL, NULL, 150, 120000),
('P009', 'Dầu gội Clear 650ml', 'Thùng', 'Chai', 12, 25, 1080000),
('P010', 'Kem đánh răng PS 200g', 'Thùng', 'Tuýp', 36, 35, 540000),
('P011', 'Nước tương Maggi 700ml', 'Thùng', 'Chai', 12, 45, 300000),
('P012', 'Bột ngọt Ajinomoto 400g', 'Thùng', 'Gói', 20, 55, 280000),
('P013', 'Cà phê G7 hòa tan', 'Thùng', 'Hộp', 24, 40, 720000),
('P014', 'Bánh Oreo 133g', 'Thùng', 'Gói', 24, 30, 360000),
('P015', 'Nước rửa chén Sunlight 750ml', 'Thùng', 'Chai', 12, 38, 300000);

-- Customers
INSERT INTO Customer (CID, CName, Address, IDNumber, Phone) VALUES
('C001', 'Tạp hóa Thanh Hằng', 'Chợ Hòa Khánh, Liên Chiểu, Đà Nẵng', '201456789', '0905111222'),
('C002', 'Cửa hàng Minh Tâm', '45 Nguyễn Lương Bằng, Liên Chiểu, Đà Nẵng', '201567890', '0912333444'),
('C003', 'Siêu thị mini Phước Lộc', '123 Tôn Đức Thắng, Liên Chiểu, Đà Nẵng', '201678901', '0935555666'),
('C004', 'Đại lý Hương Giang', 'Chợ Túy Loan, Hòa Phong, Hòa Vang, Đà Nẵng', '201789012', '0978777888'),
('C005', 'Tạp hóa Bảo Ngọc', '78 Hoàng Văn Thái, Liên Chiểu, Đà Nẵng', '201890123', '0906222333'),
('C006', 'Cửa hàng Quốc Thắng', '200 Nguyễn Sinh Sắc, Liên Chiểu, Đà Nẵng', '201901234', '0919444555'),
('C007', 'Tạp hóa Kim Liên', 'Chợ Hòa Minh, Liên Chiểu, Đà Nẵng', '202012345', '0938666777'),
('C008', 'Đại lý Phú Quý', '56 Nguyễn Hữu Thọ, Hải Châu, Đà Nẵng', '202123456', '0977888999');

-- Dealers (suppliers)
INSERT INTO Dealer (DID, DName) VALUES
('D001', 'Công ty TNHH Masan'),
('D002', 'Công ty CP Tường An'),
('D003', 'Công ty CP Vinamilk'),
('D004', 'Công ty TNHH Unilever Việt Nam'),
('D005', 'Công ty CP Ajinomoto Việt Nam');

-- Salespersons
INSERT INTO Salesperson (SID, SName, Phone) VALUES
('S001', 'Nguyễn Văn An', '0901234567'),
('S002', 'Trần Thị Bích', '0912345678'),
('S003', 'Lê Hoàng Nam', '0923456789');

-- Invoices (sales orders) with details
-- Discount columns store AMOUNTS (not percentages)
-- Calculation: line_total = qty * price - line_discount
--              total = subtotal - order_discount

-- I00001: Thanh Hằng - no discounts
-- 3*360,000 + 5*105,000 + 15*22,000 = 1,080,000 + 525,000 + 330,000 = 1,935,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00001', 'C001', 'S001', '2026-04-01', 0, 1935000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00001', 'P001', 'Thùng', 3, 360000, 0),
('I00001', 'P003', 'Thùng', 5, 105000, 0),
('I00001', 'P007', 'Bao', 15, 22000, 0);

-- I00002: Minh Tâm - order discount 70,800 (5% of 1,416,000)
-- subtotal = 2*540,000 + 1*336,000 = 1,416,000; total = 1,416,000 - 70,800 = 1,345,200
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00002', 'C002', 'S002', '2026-04-02', 70800, 1345200);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00002', 'P002', 'Thùng', 2, 540000, 0),
('I00002', 'P004', 'Thùng', 1, 336000, 0);

-- I00003: Phước Lộc - line discount 64,800 on Coca (10% of 3*216,000)
-- subtotal = (648,000-64,800) + 210,000 + 600,000 = 1,393,200
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00003', 'C003', 'S001', '2026-04-03', 0, 1393200);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00003', 'P006', 'Thùng', 3, 216000, 64800),
('I00003', 'P003', 'Thùng', 2, 105000, 0),
('I00003', 'P008', 'Bao', 5, 120000, 0);

-- I00004: Hương Giang - no discounts
-- 2*320,000 + 1*1,080,000 = 640,000 + 1,080,000 = 1,720,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00004', 'C004', 'S003', '2026-04-05', 0, 1720000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00004', 'P005', 'Thùng', 2, 320000, 0),
('I00004', 'P009', 'Thùng', 1, 1080000, 0);

-- I00005: Bảo Ngọc - line discount 72,000 on cà phê (5% of 1,440,000), order discount 158,800 (10% of 1,588,000)
-- subtotal = (1,440,000-72,000) + 220,000 = 1,588,000; total = 1,588,000 - 158,800 = 1,429,200
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00005', 'C005', 'S002', '2026-04-07', 158800, 1429200);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00005', 'P013', 'Thùng', 2, 720000, 72000),
('I00005', 'P007', 'Bao', 10, 22000, 0);

-- I00006: Thanh Hằng - no discounts
-- 10*105,000 + 3*300,000 = 1,050,000 + 900,000 = 1,950,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00006', 'C001', 'S001', '2026-04-08', 0, 1950000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00006', 'P003', 'Thùng', 10, 105000, 0),
('I00006', 'P011', 'Thùng', 3, 300000, 0);

-- I00007: Quốc Thắng - line discount 54,000 on kem đánh răng (5% of 1,080,000)
-- subtotal = (1,080,000-54,000) + 360,000 = 1,386,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00007', 'C006', 'S003', '2026-04-09', 0, 1386000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00007', 'P010', 'Thùng', 2, 540000, 54000),
('I00007', 'P014', 'Thùng', 1, 360000, 0);

-- I00008: Kim Liên - order discount 60,000 (3% of 2,000,000)
-- subtotal = 4*360,000 + 2*280,000 = 2,000,000; total = 2,000,000 - 60,000 = 1,940,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00008', 'C007', 'S002', '2026-04-10', 60000, 1940000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00008', 'P001', 'Thùng', 4, 360000, 0),
('I00008', 'P012', 'Thùng', 2, 280000, 0);

-- I00009: Phước Lộc - no discounts, uses Unit2 (Chai)
-- 20*30,000 + 3*300,000 = 600,000 + 900,000 = 1,500,000
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00009', 'C003', 'S001', '2026-04-11', 0, 1500000);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00009', 'P001', 'Chai', 20, 30000, 0),
('I00009', 'P015', 'Thùng', 3, 300000, 0);

-- I00010: Phú Quý - order discount 164,400 (5% of 3,288,000)
-- subtotal = 5*216,000 + 3*336,000 + 10*120,000 = 3,288,000; total = 3,288,000 - 164,400 = 3,123,600
INSERT INTO Invoices (InvoiceID, CID, SalespersonID, InvoiceDate, Discount, TotalAmt) VALUES
('I00010', 'C008', 'S003', '2026-04-12', 164400, 3123600);
INSERT INTO InvoiceDetails (InvoiceID, PID, SelectedUnit, Quantity, Price, Discount) VALUES
('I00010', 'P006', 'Thùng', 5, 216000, 0),
('I00010', 'P004', 'Thùng', 3, 336000, 0),
('I00010', 'P008', 'Bao', 10, 120000, 0);

-- Purchases (restocking from suppliers)

-- U00001: Masan - nước mắm + nước tương
-- 15*320,000 + 10*260,000 = 4,800,000 + 2,600,000 = 7,400,000
INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES
('U00001', 'D001', '2026-03-25', 7400000);
INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES
('U00001', 'P001', 'Thùng', 15, 320000),
('U00001', 'P011', 'Thùng', 10, 260000);

-- U00002: Tường An - dầu ăn
-- 10*480,000 = 4,800,000
INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES
('U00002', 'D002', '2026-03-26', 4800000);
INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES
('U00002', 'P002', 'Thùng', 10, 480000);

-- U00003: Vinamilk - sữa
-- 15*300,000 = 4,500,000
INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES
('U00003', 'D003', '2026-03-27', 4500000);
INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES
('U00003', 'P004', 'Thùng', 15, 300000);

-- U00004: Unilever - bột giặt + dầu gội + nước rửa chén
-- 10*280,000 + 5*960,000 + 10*260,000 = 2,800,000 + 4,800,000 + 2,600,000 = 10,200,000
INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES
('U00004', 'D004', '2026-03-28', 10200000);
INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES
('U00004', 'P005', 'Thùng', 10, 280000),
('U00004', 'P009', 'Thùng', 5, 960000),
('U00004', 'P015', 'Thùng', 10, 260000);

-- U00005: Ajinomoto - bột ngọt + mì
-- 15*240,000 + 20*90,000 = 3,600,000 + 1,800,000 = 5,400,000
INSERT INTO Purchases (PurchaseID, DID, PurchaseDate, TotalAmt) VALUES
('U00005', 'D005', '2026-04-01', 5400000);
INSERT INTO PurchaseDetails (PurchaseID, PID, SelectedUnit, Quantity, Price) VALUES
('U00005', 'P012', 'Thùng', 15, 240000),
('U00005', 'P003', 'Thùng', 20, 90000);

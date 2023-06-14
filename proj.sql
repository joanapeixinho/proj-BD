
-- populate.sql

-- Inserção de dados na tabela "customer"
INSERT INTO customer (cust_no, name, email, phone, address) VALUES
(1, 'John Smith', 'john.smith@example.com', '123456789', 'Rua da Liberdade, 1100-001 Lisboa'),
(2, 'Mary Johnson', 'mary.johnson@example.com', '987654321', 'Avenida dos Aliados, 4000-064 Porto'),
(3, 'Michael Brown', 'michael.brown@example.com', '555555555', 'Praça do Comércio, 1100-148 Lisboa'),
(4, 'Sarah Johnson', 'sarah.johnson@example.com', '111111111', 'Rua Augusta, 1100-053 Lisboa'),
(5, 'Robert Davis', 'robert.davis@example.com', '222222222', 'Rua de Santa Catarina, 4000-447 Porto'),
(6, 'Laura Wilson', 'laura.wilson@example.com', '333333333', 'Avenida da Liberdade, 1250-096 Lisboa'),
(7, 'William Thompson', 'william.thompson@example.com', '444444444', 'Rua de Cedofeita, 4050-179 Porto'),
(8, 'Emma Anderson', 'emma.anderson@example.com', '555555555', 'Rua do Carmo, 1200-093 Lisboa'),
(9, 'David Garcia', 'david.garcia@example.com', '666666666', 'Rua Mouzinho da Silveira, 4050-416 Porto'),
(10, 'Olivia Martin', 'olivia.martin@example.com', '777777777', 'Praça Luís de Camões, 1200-243 Lisboa');


-- Inserção de dados na tabela "orders"
INSERT INTO orders (order_no, cust_no, date) VALUES
(1, 1, '2021-01-10'),
(2, 2, '2021-02-15'),
(3, 3, '2021-03-20'),
(4, 4, '2021-04-25'),
(5, 5, '2021-05-30'),
(6, 6, '2021-06-05'),
(7, 7, '2021-07-10'),
(8, 8, '2022-01-20'),
(9, 9, '2022-01-20'),
(10, 10, '2022-02-25'),
(11, 1, '2022-03-25'),
(12, 5, '2022-03-25'),
(13, 4, '2022-04-25'),
(14, 2, '2022-07-25'),
(15, 3, '2022-12-25');


-- Inserção de dados na tabela "pay"
INSERT INTO pay (order_no, cust_no) VALUES
(1, 1),
(2, 2),
(3,3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10);

-- Inserção de dados na tabela "employee"
INSERT INTO employee (ssn, TIN, bdate, name) VALUES
('111111111', 'TIN111', '1992-03-18', 'Sarah Wilson'),
('222222222', 'TIN222', '1985-06-25', 'Robert Johnson'),
('333333333', 'TIN333', '2003-09-12', 'Laura Davis'),
('444444444', 'TIN444', '1988-12-05', 'William Anderson'),
('555555555', 'TIN555', '1987-04-15', 'Emma Garcia'),
('666666666', 'TIN666', '1993-07-21', 'David Thompson'),
('777777777', 'TIN777', '1989-10-28', 'Olivia Martin');

-- Inserção de dados na tabela "process"
INSERT INTO process (ssn, order_no) VALUES
('111111111', 4),
('222222222', 5),
('333333333', 6),
('444444444', 7),
('555555555', 8),
('666666666', 9),
('666666666', 10),
('666666666', 11),
('666666666', 12),
('666666666', 13),
('666666666', 14),
('666666666', 15);

-- Inserção de dados na tabela "department"
INSERT INTO department (name) VALUES
('Sales'),
('Finance'),
('Marketing'),
('Human Resources'),
('IT'),
('Operations'),
('Customer Service');

-- Inserção de dados na tabela "workplace"
INSERT INTO workplace (address, lat, long) VALUES
('123 Main St', 12.345678, -98.765432),
('456 Elm St', 23.456789, -87.654321),
('789 Oak St', 34.567890, -76.543210),
('321 Cedar St', 45.678901, -65.432109),
('654 Pine St', 56.789012, -54.321098),
('876 Maple St', 67.890123, -43.210987),
('543 Birch St', 78.901234, -32.109876);

INSERT INTO office (address) VALUES
('123 Main St'),
('456 Elm St'),
('789 Oak St');

-- Inserção de dados na tabela "warehouse"
INSERT INTO warehouse (address) VALUES
('321 Cedar St'),
('654 Pine St'),
('876 Maple St'),
('543 Birch St');


-- Inserção de dados na tabela "works"
INSERT INTO works (ssn, name, address) VALUES
('111111111', 'Sales', '123 Main St'),
('222222222', 'Finance', '456 Elm St'),
('333333333', 'Marketing', '789 Oak St'),
('444444444', 'Human Resources', '321 Cedar St'),
('555555555', 'IT', '654 Pine St'),
('666666666', 'Operations', '876 Maple St'),
('777777777', 'Customer Service', '543 Birch St');

-- Inserção de dados na tabela "product"
INSERT INTO product (SKU, name, description, price, ean) VALUES
('SKU001', 'Product 1', 'Description 1', 9.99, 1234567890123),
('SKU002', 'Product 2', 'Description 2', 12.99, 9876543210987),
('SKU003', 'Product 3', 'Description 3', 15.99, 1234567890124),
('SKU004', 'Product 4', 'Description 4', 9.99, 9876543210986),
('SKU005', 'Product 5', 'Description 5', 12.99, 1111111111111),
('SKU006', 'Product 6', 'Description 6', 8.99, 2222222222222),
('SKU007', 'Product 7', 'Description 7', 19.99, 3333333333333),
('SKU008', 'Product 8', 'Description 8', 14.99, 4444444444444),
('SKU009', 'Product 9', 'Description 9', 11.99, 5555555555555),
('SKU010', 'Product 10', 'Description 10', 17.99, 6666666666666),
('SKU011', 'Product 11', 'Description 11', 9.99, 7777777777777),
('SKU012', 'Product 12', 'Description 12', 14.99, 8888888888888),
('SKU013', 'Product 13', 'Description 13', 11.99, 9999999999999),
('SKU014', 'Product 14', 'Description 14', 7.99, 1010101010101);

-- Inserção de dados na tabela "contains"
INSERT INTO contains (order_no, SKU, qty) VALUES
(1, 'SKU001', 2),
(2, 'SKU002', 1),
(3, 'SKU003', 3),
(4, 'SKU004', 2),
(5, 'SKU005', 1),
(6, 'SKU006', 4),
(7, 'SKU007', 3),
(8, 'SKU008', 2),
(9, 'SKU009', 1),
(10, 'SKU010', 3),
(1, 'SKU011', 2),
(2, 'SKU012', 1),
(3, 'SKU013', 4),
(4, 'SKU014', 3),
(5, 'SKU001', 2),
(6, 'SKU002', 1),
(7, 'SKU003', 3),
(8, 'SKU004', 2),
(9, 'SKU005', 1),
(10, 'SKU006', 4),
(1, 'SKU007', 3),
(2, 'SKU008', 2),
(3, 'SKU009', 1),
(4, 'SKU010', 3),
(5, 'SKU011', 2),
(6, 'SKU012', 1),
(7, 'SKU013', 4),
(8, 'SKU014', 3),
(9, 'SKU001', 2),
(10, 'SKU002', 1),
(1, 'SKU003', 3),
(2, 'SKU004', 2),
(3, 'SKU005', 1),
(4, 'SKU006', 4),
(5, 'SKU007', 3),
(6, 'SKU008', 2),
(7, 'SKU009', 1),
(8, 'SKU010', 3),
(9, 'SKU011', 2),
(10, 'SKU012', 1),
(1, 'SKU013', 4),
(2, 'SKU014', 3),
(3, 'SKU001', 2),
(4, 'SKU002', 1),
(5, 'SKU003', 3),
(6, 'SKU004', 2),
(7, 'SKU005', 1),
(8, 'SKU006', 4),
(9, 'SKU007', 3),
(10, 'SKU008', 2),
(1, 'SKU009', 1),
(2, 'SKU010', 3),
(3, 'SKU011', 2),
(4, 'SKU012', 1),
(5, 'SKU013', 4),
(6, 'SKU014', 3),
(7, 'SKU001', 2),
(8, 'SKU002', 1),
(9, 'SKU003', 3),
(10, 'SKU004', 2);

-- Inserção de dados na tabela "supplier"
INSERT INTO supplier (TIN, name, address, SKU, date) VALUES
('TIN001', 'Supplier 1', '123 Supplier St', 'SKU001', '2022-01-01'),
('TIN002', 'Supplier 2', '456 Supplier St', 'SKU002', '2022-02-05'),
('TIN003', 'Supplier 3', '789 Supplier St', 'SKU003', '2022-03-10'),
('TIN004', 'Supplier 4', '321 Supplier St', 'SKU004', '2022-04-15'),
('TIN005', 'Supplier 5', '654 Supplier St', 'SKU005', '2022-05-20'),
('TIN006', 'Supplier 6', '876 Supplier St', 'SKU006', '2022-06-25'),
('TIN007', 'Supplier 7', '543 Supplier St', 'SKU007', '2022-07-30');

-- Inserção de dados na tabela "delivery"
INSERT INTO delivery (address, TIN) VALUES
('321 Cedar St', 'TIN001'),
('654 Pine St', 'TIN002'),
('876 Maple St', 'TIN003'),
('543 Birch St', 'TIN004');

INSERT INTO product_photos (product_sku, photo_url)
VALUES 
    ('SKU001', 'static/images/product1.jpg'),
    ('SKU002', 'static/images/product2.jpg'),
    ('SKU003', 'static/images/product3.jpg'),
    ('SKU004', 'static/images/product4.jpg'),
    ('SKU005', 'static/images/product5.jpg'),
    ('SKU006', 'static/images/product6.jpg'),
    ('SKU007', 'static/images/product7.jpg'),
    ('SKU008', 'static/images/product8.jpg'),
    ('SKU009', 'static/images/product9.jpg'),
    ('SKU010', 'static/images/product10.jpg'),
    ('SKU011', 'static/images/product11.jpg'),
    ('SKU012', 'static/images/product12.jpg'),
    ('SKU013', 'static/images/product13.jpg'),
    ('SKU014', 'static/images/product14.jpg'),
    ('SKU015', 'static/images/product15.jpg'),
    ('SKU016', 'static/images/product16.jpg'),
    ('SKU017', 'static/images/product17.jpg'),
    ('SKU018', 'static/images/product18.jpg'),
    ('SKU019', 'static/images/product19.jpg'),
    ('SKU020', 'static/images/product20.jpg');
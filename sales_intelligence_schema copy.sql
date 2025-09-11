-- =========================================================
-- DROP TABLES IF THEY EXIST (in dependency order)
-- =========================================================
DROP TABLE IF EXISTS campaign_responses;
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_taxonomy;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS competitors;

-- =========================================================
-- 1. MASTER / CATEGORICAL TABLES
-- =========================================================

-- 1.1 Regions Table
CREATE TABLE IF NOT EXISTS regions (
    region_id STRING NOT NULL,
    region_name STRING,
    country STRING,
    geo_cluster STRING,
    CONSTRAINT pk_regions PRIMARY KEY (region_id)
) USING DELTA;

INSERT INTO regions VALUES
('R001', 'North America', 'USA', 'AMER'),
('R002', 'Europe West', 'Germany', 'EMEA'),
('R003', 'Europe East', 'Poland', 'EMEA'),
('R004', 'APAC North', 'Japan', 'APAC'),
('R005', 'APAC South', 'India', 'APAC'),
('R006', 'Africa West', 'Nigeria', 'MEA'),
('R007', 'Africa East', 'Kenya', 'MEA'),
('R008', 'South America', 'Brazil', 'LATAM'),
('R009', 'Middle East', 'UAE', 'MEA'),
('R010', 'Oceania', 'Australia', 'APAC');

-- 1.2 Product Taxonomy Table
CREATE TABLE IF NOT EXISTS product_taxonomy (
    category_id STRING NOT NULL,
    category_name STRING,
    parent_category_id STRING,
    tags ARRAY<STRING>,
    CONSTRAINT pk_product_taxonomy PRIMARY KEY (category_id)
) USING DELTA;

INSERT INTO product_taxonomy VALUES
('C001', '5G IoT Platforms', NULL, ARRAY('5G','IoT','Platform')),
('C002', 'Smartphones', NULL, ARRAY('5G','Mobile')),
('C003', 'Wearables', NULL, ARRAY('IoT','Fitness')),
('C004', 'Edge Devices', NULL, ARRAY('Edge','IoT')),
('C005', 'Networking', NULL, ARRAY('5G','Infra')),
('C006', 'Cloud AI Services', NULL, ARRAY('AI','Cloud')),
('C007', 'Automotive IoT', NULL, ARRAY('IoT','Automotive')),
('C008', 'Industrial IoT', NULL, ARRAY('IoT','Manufacturing')),
('C009', 'Healthcare IoT', NULL, ARRAY('IoT','Healthcare')),
('C010', 'Consumer IoT', NULL, ARRAY('IoT','Home'));

-- 1.3 Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id STRING NOT NULL,
    product_name STRING,
    category_id STRING NOT NULL,
    launch_date DATE,
    price DECIMAL(10,2),
    status STRING,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES product_taxonomy(category_id)
) USING DELTA;

INSERT INTO products VALUES
('P001', 'Snapdragon X Elite', 'C001', '2024-03-01', 350.00, 'Active'),
('P002', 'Snapdragon Edge AI', 'C004', '2024-01-15', 499.00, 'Active'),
('P003', 'IoT Connect Pro', 'C001', '2023-12-01', 299.00, 'Active'),
('P004', 'HealthSense Band', 'C003', '2023-08-10', 199.00, 'Active'),
('P005', 'AutoTrack IoT', 'C007', '2024-02-20', 599.00, 'Active'),
('P006', 'EdgeHub Mini', 'C004', '2024-05-01', 450.00, 'Planned'),
('P007', 'CloudAI Core', 'C006', '2023-10-01', 799.00, 'Active'),
('P008', 'HomeSense Hub', 'C010', '2023-09-15', 250.00, 'Active'),
('P009', 'FactoryVision IoT', 'C008', '2024-06-01', 950.00, 'Planned'),
('P010', 'MediSense IoT', 'C009', '2024-03-20', 620.00, 'Active');

-- 1.4 Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id STRING NOT NULL,
    customer_name STRING,
    segment STRING,
    email STRING,
    phone STRING,
    region_id STRING NOT NULL,
    partner_id STRING,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT fk_customers_region FOREIGN KEY (region_id) REFERENCES regions(region_id)
) USING DELTA;

INSERT INTO customers VALUES
('CUST001','Acme Corp','Enterprise','acme@corp.com','+1-202-555-0101','R001','PR001'),
('CUST002','Zenith Tech','SMB','contact@zenith.com','+49-202-555-0102','R002','PR002'),
('CUST003','Kaito Solutions','Enterprise','kaito@solutions.jp','+81-202-555-0103','R004','PR003'),
('CUST004','Innova Systems','Mid-Market','innova@sys.com','+91-202-555-0104','R005','PR004'),
('CUST005','Nova Health','SMB','nova@health.com','+61-202-555-0105','R010','PR005'),
('CUST006','UrbanWear Ltd','Mid-Market','urban@wear.co.uk','+44-202-555-0106','R002','PR006'),
('CUST007','Cloudify AI','Enterprise','cloud@ify.ai','+1-202-555-0107','R001','PR007'),
('CUST008','SmartEdge','SMB','smart@edge.com','+55-202-555-0108','R008','PR008'),
('CUST009','IoTGlobal','Enterprise','info@iotglobal.com','+971-202-555-0109','R009','PR009'),
('CUST010','NextWave Inc','SMB','hello@nextwave.com','+61-202-555-0110','R010','PR010');

-- 1.5 Competitors Table
CREATE TABLE IF NOT EXISTS competitors (
    competitor_id STRING NOT NULL,
    competitor_name STRING,
    hq_region STRING,
    website STRING,
    CONSTRAINT pk_competitors PRIMARY KEY (competitor_id)
) USING DELTA;

INSERT INTO competitors VALUES
('COMP001','Qualcomm','USA','https://www.qualcomm.com'),
('COMP002','Huawei','China','https://www.huawei.com'),
('COMP003','Samsung','South Korea','https://www.samsung.com'),
('COMP004','Ericsson','Sweden','https://www.ericsson.com'),
('COMP005','Nokia','Finland','https://www.nokia.com');

-- =========================================================
-- 2. TRANSACTIONAL TABLES
-- =========================================================

-- 2.1 Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    order_date DATE,
    region_id STRING NOT NULL,
    total_amount DECIMAL(12,2),
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_orders_region FOREIGN KEY (region_id) REFERENCES regions(region_id)
) USING DELTA;

INSERT INTO orders
SELECT
    CONCAT('O', LPAD(CAST(id AS STRING), 3, '0')) AS order_id,
    CONCAT('CUST', LPAD(CAST(1 + (RAND() * 10) AS INT), 3, '0')) AS customer_id,
    DATEADD(DAY, -CAST(RAND() * 365 AS INT), CURRENT_DATE) AS order_date,
    CONCAT('R', LPAD(CAST(1 + (RAND() * 10) AS INT), 3, '0')) AS region_id,
    ROUND(100 + RAND() * 5000, 2) AS total_amount
FROM range(1, 121) AS t(id);

-- 2.2 Order Lines Table
CREATE TABLE IF NOT EXISTS order_lines (
    order_line_id STRING NOT NULL,
    order_id STRING NOT NULL,
    product_id STRING NOT NULL,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(5,2),
    net_amount DECIMAL(10,2),
    CONSTRAINT pk_order_lines PRIMARY KEY (order_line_id),
    CONSTRAINT fk_order_lines_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_order_lines_product FOREIGN KEY (product_id) REFERENCES products(product_id)
) USING DELTA;

INSERT INTO order_lines
SELECT
    CONCAT('OL', LPAD(CAST(id AS STRING), 3, '0')) AS order_line_id,
    CONCAT('O', LPAD(CAST(1 + (RAND() * 120) AS INT), 3, '0')) AS order_id,
    CONCAT('P', LPAD(CAST(1 + (RAND() * 10) AS INT), 3, '0')) AS product_id,
    CAST(1 + (RAND() * 5) AS INT) AS quantity,
    ROUND(150 + RAND() * 800, 2) AS unit_price,
    ROUND(RAND() * 15, 2) AS discount,
    ROUND((quantity * unit_price) - discount, 2) AS net_amount
FROM range(1, 350) AS t(id);

-- 2.3 Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id STRING NOT NULL,
    order_id STRING NOT NULL,
    ship_date DATE,
    delivery_date DATE,
    status STRING,
    carrier STRING,
    CONSTRAINT pk_shipments PRIMARY KEY (shipment_id)
) USING DELTA;

INSERT INTO shipments
SELECT
    CONCAT('S', LPAD(CAST(id AS STRING), 3, '0')) AS shipment_id,
    CONCAT('O', LPAD(CAST(1 + (RAND() * 120) AS INT), 3, '0')) AS order_id,
    DATEADD(DAY, -CAST(RAND() * 300 AS INT), CURRENT_DATE) AS ship_date,
    DATEADD(DAY, CAST(RAND() * 7 AS INT), ship_date) AS delivery_date,
    CASE WHEN RAND() < 0.8 THEN 'Delivered' ELSE 'In Transit' END AS status,
    CASE WHEN RAND() < 0.5 THEN 'DHL' ELSE 'FedEx' END AS carrier
FROM range(1, 250) AS t(id);

-- 2.4 Returns Table
CREATE TABLE IF NOT EXISTS returns (
    return_id STRING NOT NULL,
    order_line_id STRING NOT NULL,
    return_date DATE,
    reason STRING,
    refund_amount DECIMAL(10,2),
    CONSTRAINT pk_returns PRIMARY KEY (return_id),
    CONSTRAINT fk_returns_order_line FOREIGN KEY (order_line_id) REFERENCES order_lines(order_line_id)
) USING DELTA;

INSERT INTO returns
SELECT
    CONCAT('R', LPAD(CAST(id AS STRING), 3, '0')) AS return_id,
    CONCAT('OL', LPAD(CAST(1 + (RAND() * 250) AS INT), 3, '0')) AS order_line_id,
    DATEADD(DAY, -CAST(RAND() * 180 AS INT), CURRENT_DATE) AS return_date,
    CASE
        WHEN RAND() < 0.4 THEN 'Defective'
        WHEN RAND() < 0.7 THEN 'Wrong Item'
        ELSE 'Customer Dissatisfaction'
    END AS reason,
    ROUND(50 + RAND() * 600, 2) AS refund_amount
FROM range(1, 100) AS t(id);

-- 2.5 Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id STRING NOT NULL,
    campaign_name STRING,
    start_date DATE,
    end_date DATE,
    target_segment STRING,
    CONSTRAINT pk_campaigns PRIMARY KEY (campaign_id)
) USING DELTA;

INSERT INTO campaigns VALUES
('CAM001','5G IoT Expansion','2024-01-01','2024-03-31','Enterprise'),
('CAM002','Wearable Awareness','2024-02-15','2024-04-30','SMB'),
('CAM003','Edge Devices Push','2024-03-01','2024-06-30','Enterprise'),
('CAM004','Healthcare IoT Drive','2024-04-01','2024-07-15','Mid-Market'),
('CAM005','Consumer IoT Summer','2024-05-01','2024-08-31','SMB');

-- 2.6 Campaign Responses Table
CREATE TABLE IF NOT EXISTS campaign_responses (
    response_id STRING NOT NULL,
    campaign_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    response_date DATE,
    response_type STRING,
    CONSTRAINT pk_campaign_responses PRIMARY KEY (response_id),
    CONSTRAINT fk_campaign_responses_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CONSTRAINT fk_campaign_responses_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) USING DELTA;

INSERT INTO campaign_responses
SELECT
    CONCAT('RESP', LPAD(CAST(id AS STRING), 3, '0')) AS response_id,
    CONCAT('CAM', LPAD(CAST(1 + (RAND() * 5) AS INT), 3, '0')) AS campaign_id,
    CONCAT('CUST', LPAD(CAST(1 + (RAND() * 10) AS INT), 3, '0')) AS customer_id,
    DATEADD(DAY, -CAST(RAND() * 60 AS INT), CURRENT_DATE) AS response_date,
    CASE WHEN RAND() < 0.6 THEN 'Clicked' ELSE 'Purchased' END AS response_type
FROM range(1, 120) AS t(id);

-- =========================================================
-- 3. DERIVED GRAPH-ORIENTED VIEWS (For Graph-RAG)
-- =========================================================

-- 3.1 Customer → Product Relationships
CREATE OR REPLACE VIEW v_customer_product AS
SELECT
    o.customer_id,
    ol.product_id,
    COUNT(DISTINCT o.order_id) AS order_count,
    MAX(o.order_date) AS last_purchase_date
FROM orders o
JOIN order_lines ol ON o.order_id = ol.order_id
GROUP BY o.customer_id, ol.product_id;

-- 3.2 Product → Region KPIs
CREATE OR REPLACE VIEW v_product_region AS
SELECT
    ol.product_id,
    o.region_id,
    SUM(ol.quantity) AS units_sold,
    ROUND(SUM(ol.net_amount), 2) AS revenue,
    ROUND((SUM(ol.quantity) / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2) AS growth_rate
FROM orders o
JOIN order_lines ol ON o.order_id = ol.order_id
GROUP BY ol.product_id, o.region_id;

-- 3.3 Product → Competitor Overlap
CREATE OR REPLACE VIEW v_product_competitor AS
SELECT
    p.product_id,
    c.competitor_id,
    ROUND(RAND() * 100, 2) AS overlap_score
FROM products p
CROSS JOIN competitors c;
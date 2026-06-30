-- ============================================================
--  Online Retail Analytics — Database Schema (PostgreSQL)
-- ============================================================

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders      CASCADE;
DROP TABLE IF EXISTS products    CASCADE;
DROP TABLE IF EXISTS categories  CASCADE;
DROP TABLE IF EXISTS customers   CASCADE;

-- ── CATEGORIES ──────────────────────────────────────────────
CREATE TABLE categories (
    category_id     INTEGER       PRIMARY KEY,
    category_name   VARCHAR(80)   NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ── CUSTOMERS ───────────────────────────────────────────────
CREATE TABLE customers (
    customer_id    INTEGER      PRIMARY KEY,
    customer_name VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    phone         VARCHAR(20),
    city          VARCHAR(80),
    state         VARCHAR(80),
    gender        VARCHAR(10)   CHECK (gender IN ('Male','Female','Other')),
    age           SMALLINT      CHECK (age >= 0 AND age <= 120),
    signup_date   DATE          NOT NULL DEFAULT CURRENT_DATE,
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE
);

-- ── PRODUCTS ────────────────────────────────────────────────
CREATE TABLE products (
    product_id     INTEGER          PRIMARY KEY,
    category_id    INTEGER         NOT NULL,
    product_name   VARCHAR(150)    NOT NULL,
    brand          VARCHAR(80),
    unit_price     NUMERIC(10,2)   NOT NULL CHECK (unit_price >= 0),
    stock_quantity INTEGER         NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON DELETE RESTRICT
);

-- ── ORDERS ──────────────────────────────────────────────────
CREATE TABLE orders (
    order_id        INTEGER         PRIMARY KEY,
    customer_id     INTEGER        NOT NULL,
    order_date      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(20)    NOT NULL DEFAULT 'pending'
                                   CHECK (status IN ('pending','processing','shipped','delivered','cancelled')),
    total_amount    NUMERIC(10,2)  NOT NULL CHECK (total_amount >= 0),
    discount_amount NUMERIC(10,2)  NOT NULL DEFAULT 0,
    shipping_city   VARCHAR(80),
    shipping_state  VARCHAR(80),
    payment_method  VARCHAR(30),
    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        ON DELETE RESTRICT
);

-- ── ORDER ITEMS (junction table) ───────────────────────────
CREATE TABLE order_items (
    item_id      INTEGER          PRIMARY KEY,
    order_id     INTEGER         NOT NULL,
    product_id   INTEGER         NOT NULL,
    quantity     SMALLINT        NOT NULL CHECK (quantity > 0),
    unit_price   NUMERIC(10,2)   NOT NULL CHECK (unit_price >= 0),
    discount_pct NUMERIC(5,2)    NOT NULL DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct <= 100),
    CONSTRAINT fk_item_order
        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    CONSTRAINT fk_item_product
        FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE RESTRICT
);

-- ── INDEXES ─────────────────────────────────────────────────
CREATE INDEX idx_orders_customer_id  ON orders (customer_id);
CREATE INDEX idx_orders_date         ON orders (order_date);
CREATE INDEX idx_order_items_order   ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);
CREATE INDEX idx_products_category   ON products (category_id);

-- ── VIEWS ───────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    DATE_TRUNC('month', order_date)::date AS month,
    COUNT(DISTINCT order_id)              AS total_orders,
    COUNT(DISTINCT customer_id)           AS unique_customers,
    SUM(total_amount)                     AS revenue,
    ROUND(AVG(total_amount), 2)           AS avg_order_value
FROM orders
WHERE status != 'cancelled'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

CREATE OR REPLACE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    p.brand,
    SUM(oi.quantity)                  AS total_units_sold,
    SUM(oi.quantity * oi.unit_price)  AS total_revenue,
    COUNT(DISTINCT oi.order_id)       AS times_ordered
FROM products p
JOIN categories c   ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders o        ON oi.order_id   = o.order_id
WHERE o.status != 'cancelled'
GROUP BY p.product_id, p.product_name, c.category_name, p.brand;

CREATE OR REPLACE VIEW vw_customer_ltv AS
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    c.gender,
    c.age,
    COUNT(DISTINCT o.order_id)            AS total_orders,
    COALESCE(SUM(o.total_amount), 0)      AS lifetime_value,
    COALESCE(ROUND(AVG(o.total_amount),2),0) AS avg_order_value,
    MIN(o.order_date)                     AS first_order_date,
    MAX(o.order_date)                     AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status != 'cancelled'
GROUP BY c.customer_id, c.customer_name, c.city, c.state, c.gender, c.age;

CREATE OR REPLACE VIEW vw_category_sales AS
SELECT
    c.category_name,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    SUM(oi.quantity)                 AS total_units_sold,
    COUNT(DISTINCT o.order_id)       AS total_orders
FROM categories c
JOIN products p      ON c.category_id = p.category_id
JOIN order_items oi  ON p.product_id  = oi.product_id
JOIN orders o         ON oi.order_id   = o.order_id
WHERE o.status != 'cancelled'
GROUP BY c.category_name;

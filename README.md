# Online Retail Analytics Dashboard

A full-stack data analytics project: PostgreSQL → Python ETL → Streamlit Dashboard.

## Project Structure
```
retail_dashboard/
├── sql/
│   └── schema.sql          # Tables, constraints, indexes, views
├── data/                   # Generated sample CSVs (auto-created)
├── etl/
│   ├── config.py           # EDIT: your DB credentials
│   ├── generate_data.py    # Creates sample CSV data
│   └── load_data.py        # ETL: extract, clean, load into PostgreSQL
├── dashboard/
│   ├── config.py           # (copy of DB config used by the dashboard)
│   └── app.py              # Streamlit dashboard
└── requirements.txt
```

## How to run (5 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create the PostgreSQL database
Open `psql` or pgAdmin and run:
```sql
CREATE DATABASE retail_db;
```

### 3. Edit your DB credentials
Open `etl/config.py` AND `dashboard/config.py`, update:
```python
DB_USER = "postgres"
DB_PASSWORD = "your_actual_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "retail_db"
```

### 4. Build the schema, generate data, and load it
```bash
# Create tables, indexes, views
psql -U postgres -d retail_db -f sql/schema.sql

# Generate sample CSV data (~500 rows)
cd etl
python generate_data.py

# Run the ETL pipeline (clean + load into PostgreSQL)
python load_data.py
```

### 5. Launch the dashboard
```bash
cd ../dashboard
streamlit run app.py
```
Open the URL shown in your terminal (usually `http://localhost:8501`).

## What's inside the dashboard
- KPI cards: Total Revenue, Total Orders, Unique Customers, Avg Order Value
- Time-series revenue trend with 7-day rolling average
- Revenue by category (bar chart)
- Top 10 products by revenue
- Revenue by city
- Top 10 customers by lifetime value
- Order status drill-down (pie chart + table)
- Filters: date range, category, order status
- Raw data table (expandable)

## Database design summary
5 tables: `categories`, `customers`, `products`, `orders`, `order_items` (junction table).
3NF normalized. Primary/Foreign keys enforced. Indexes on all FK columns.
4 SQL views pre-aggregate common analytics queries (`vw_monthly_revenue`,
`vw_product_sales`, `vw_customer_ltv`, `vw_category_sales`).

## Notes for your review/interview
- `order_items` stores `unit_price` at time of purchase (price snapshotting) —
  protects historical order accuracy even if product prices later change.
- ETL script removes duplicate emails/order IDs, fills missing values, and
  validates referential integrity before loading (orphan-record prevention).
- Dashboard queries hit PostgreSQL directly via SQLAlchemy — no static data.

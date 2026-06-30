#  Online Retail Analytics Dashboard

## Project Overview

This project is a simple end-to-end Retail Analytics Dashboard built using **PostgreSQL, Python, Pandas, SQLAlchemy, Plotly, and Streamlit**.

The objective is to store retail sales data in a SQL database, perform data cleaning and analysis, and visualize business insights through an interactive dashboard.

---

## Technology Stack

- PostgreSQL
- Python
- Pandas
- SQLAlchemy
- Streamlit
- Plotly

---

## Project Structure

```
retail_dashboard/
│
├── dashboard/
│   ├── app.py
│   └── config.py
│
├── data/
│   ├── categories.csv
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
│
├── etl/
│   ├── generate_data.py
│   ├── load_data.py
│   └── config.py
│
├── sql/
│   └── schema.sql
│
├── requirements.txt
└── README.md
```

---

# Features

- Relational database design
- Primary Key & Foreign Key relationships
- Data Cleaning using Pandas
- ETL (Extract, Transform, Load) pipeline
- PostgreSQL database integration
- SQLAlchemy database connectivity
- Interactive Streamlit dashboard
- KPI cards
- Revenue trend analysis
- Category-wise sales analysis
- Top products analysis
- Customer Lifetime Value (LTV)
- Revenue by city
- Order status distribution
- Interactive filters

---

# Database Design

The database contains five normalized tables:

- Categories
- Customers
- Products
- Orders
- Order Items

Database features:

- Primary Keys
- Foreign Keys
- Constraints
- Indexes
- SQL Views

---

# ETL Pipeline

The ETL pipeline performs:

- Extract data from CSV files
- Remove duplicate records
- Handle missing values
- Validate data
- Load cleaned data into PostgreSQL

---

# Dashboard

The Streamlit dashboard includes:

- Total Revenue KPI
- Total Orders KPI
- Total Customers KPI
- Average Order Value
- Revenue Trend
- Revenue by Category
- Top Selling Products
- Customer Analysis
- Revenue by City
- Order Status Analysis
- Interactive Filters

---

# Installation

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Create Database

```sql
CREATE DATABASE retail_db;
```

## 3. Configure Database

Update the following files with your PostgreSQL credentials:

- etl/config.py
- dashboard/config.py

Example:

```python
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "retail_db"
```

---

## 4. Create Database Schema

Run:

```bash
psql -U postgres -d retail_db -f sql/schema.sql
```

---

## 5. Generate Sample Data

```bash
cd etl
python generate_data.py
```

---

## 6. Load Data

```bash
python load_data.py
```

---

## 7. Run Dashboard

```bash
cd ../dashboard
python -m streamlit run app.py
```

---

# Project Workflow

```
CSV Files
      │
      ▼
ETL Pipeline
      │
      ▼
Data Cleaning
      │
      ▼
PostgreSQL Database
      │
      ▼
SQL Views
      │
      ▼
Python (SQLAlchemy)
      │
      ▼
Streamlit Dashboard
      │
      ▼
Business Insights
```

---

# Business Insights

The dashboard provides insights such as:

- Monthly Revenue Trend
- Best Selling Products
- Category Performance
- Customer Lifetime Value
- Revenue Distribution by City
- Order Status Analysis
- Sales KPIs

---


**Sameeksha A**


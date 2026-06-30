"""
load_data.py
ETL pipeline: Extract CSVs -> Transform (clean) -> Load into PostgreSQL.

Usage:
    python load_data.py

Requires DB connection details in config.py (edit before running).
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_URI

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

engine = create_engine(DB_URI)
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("""
        TRUNCATE TABLE
        order_items,
        orders,
        products,
        categories,
        customers
        RESTART IDENTITY CASCADE;
    """))

print("Database cleared successfully.")


def extract(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    df = pd.read_csv(path)
    print(f"Extracted {name}: {len(df)} rows")
    return df


def clean_customers(df):
    before = len(df)
    df = df.drop_duplicates(subset=["email"])                # remove duplicate emails
    df["phone"] = df["phone"].fillna("Unknown")               # handle missing phone
    df["city"] = df["city"].fillna("Unknown")
    df["state"] = df["state"].fillna("Unknown")
    df = df.dropna(subset=["customer_name", "email"])          # critical fields must exist
    df["customer_name"] = df["customer_name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    after = len(df)
    print(f"  customers cleaned: {before} -> {after} rows")
    return df


def clean_products(df):
    before = len(df)
    df = df.drop_duplicates(subset=["product_id"])
    df = df[df["unit_price"] >= 0]                              # remove invalid prices
    df["stock_quantity"] = df["stock_quantity"].fillna(0).astype(int)
    after = len(df)
    print(f"  products cleaned: {before} -> {after} rows")
    return df


def clean_orders(df, valid_customer_ids):
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    df = df[df["customer_id"].isin(valid_customer_ids)]        # referential integrity check
    df = df[df["total_amount"] >= 0]
    df["order_date"] = pd.to_datetime(df["order_date"])
    after = len(df)
    print(f"  orders cleaned: {before} -> {after} rows")
    return df


def clean_order_items(df, valid_order_ids, valid_product_ids):
    before = len(df)
    df = df.drop_duplicates(subset=["item_id"])
    df = df[df["order_id"].isin(valid_order_ids)]
    df = df[df["product_id"].isin(valid_product_ids)]
    df = df[df["quantity"] > 0]
    after = len(df)
    print(f"  order_items cleaned: {before} -> {after} rows")
    return df


def load(df, table_name):
    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df)} rows into '{table_name}'")


def main():
    print("=== STEP 1: EXTRACT ===")
    categories = extract("categories")
    customers = extract("customers")
    products = extract("products")
    orders = extract("orders")
    order_items = extract("order_items")

    print("\n=== STEP 2: TRANSFORM (clean) ===")
    customers = clean_customers(customers)
    products = clean_products(products)
    orders = clean_orders(orders, set(customers["customer_id"]))
    order_items = clean_order_items(order_items, set(orders["order_id"]), set(products["product_id"]))

    print("\n=== STEP 3: LOAD into PostgreSQL ===")
    # Order matters: parents before children (FK dependency)
    load(categories, "categories")
    load(customers, "customers")
    load(products, "products")
    load(orders, "orders")
    load(order_items, "order_items")

    print("\n=== STEP 4: VALIDATE ===")
    with engine.connect() as conn:
        for tbl in ["categories", "customers", "products", "orders", "order_items"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"  {tbl}: {count} rows in database")

    print("\nETL pipeline completed successfully.")


if __name__ == "__main__":
    main()

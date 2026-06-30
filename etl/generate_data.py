"""
generate_data.py
Generates sample CSV files for the Online Retail Analytics project.
Run this BEFORE the ETL script. Produces ~500 rows total across all tables.
"""
import csv
import random
from datetime import datetime, timedelta
import os

random.seed(42)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- CATEGORIES ----------
categories = [
    "Electronics", "Clothing", "Home & Kitchen", "Books",
    "Sports & Fitness", "Beauty & Personal Care", "Toys & Games"
]

with open(os.path.join(OUT_DIR, "categories.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category_id", "category_name", "description"])
    for i, c in enumerate(categories, start=1):
        w.writerow([i, c, f"{c} products"])

# ---------- PRODUCTS ----------
product_names_by_cat = {
    "Electronics": ["Wireless Earbuds", "Smartphone", "Laptop", "Bluetooth Speaker", "Smartwatch", "Power Bank"],
    "Clothing": ["Cotton T-Shirt", "Denim Jeans", "Running Shoes", "Jacket", "Formal Shirt", "Sneakers"],
    "Home & Kitchen": ["Mixer Grinder", "Non-stick Pan", "LED Lamp", "Pressure Cooker", "Bedsheet Set", "Storage Box"],
    "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Biography", "Comic Book", "Notebook Set"],
    "Sports & Fitness": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Football", "Resistance Bands", "Skipping Rope"],
    "Beauty & Personal Care": ["Face Wash", "Shampoo", "Moisturizer", "Lipstick", "Perfume", "Hair Dryer"],
    "Toys & Games": ["Building Blocks", "Remote Car", "Board Game", "Puzzle Set", "Action Figure", "Soft Toy"],
}
brands = ["Generic", "PrimeBrand", "ValueCo", "EliteGoods", "DailyNeeds", "TopChoice"]

products = []
pid = 1
with open(os.path.join(OUT_DIR, "products.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["product_id", "category_id", "product_name", "brand", "unit_price", "stock_quantity", "is_active"])
    for cat_idx, cat in enumerate(categories, start=1):
        for name in product_names_by_cat[cat]:
            price = round(random.uniform(150, 60000) if cat == "Electronics" else random.uniform(99, 3000), 2)
            stock = random.randint(0, 300)
            is_active = random.random() > 0.05
            w.writerow([pid, cat_idx, name, random.choice(brands), price, stock, is_active])
            products.append({"product_id": pid, "category_id": cat_idx, "unit_price": price})
            pid += 1

# ---------- CUSTOMERS ----------
first_names = ["Priya","Rajan","Anita","Vikram","Sneha","Arjun","Kavya","Rohit","Meera","Suresh",
               "Divya","Karthik","Pooja","Manoj","Lakshmi","Sanjay","Nisha","Arvind","Deepa","Vivek"]
last_names = ["Sharma","Kumar","Patel","Singh","Reddy","Iyer","Nair","Gupta","Rao","Menon"]
cities_states = [
    ("Chennai","Tamil Nadu"), ("Mumbai","Maharashtra"), ("Delhi","Delhi"), ("Bangalore","Karnataka"),
    ("Hyderabad","Telangana"), ("Pune","Maharashtra"), ("Kolkata","West Bengal"), ("Ahmedabad","Gujarat"),
    ("Jaipur","Rajasthan"), ("Kochi","Kerala")
]

customers = []
N_CUSTOMERS = 120
with open(os.path.join(OUT_DIR, "customers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["customer_id","customer_name","email","phone","city","state","gender","age","signup_date","is_active"])
    for i in range(1, N_CUSTOMERS + 1):
        fn, ln = random.choice(first_names), random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        phone = f"9{random.randint(100000000,999999999)}"
        city, state = random.choice(cities_states)
        gender = random.choice(["Male","Female","Other"])
        age = random.randint(18, 65)
        signup_date = (datetime(2023,1,1) + timedelta(days=random.randint(0, 540))).date()
        is_active = random.random() > 0.08
        w.writerow([i, name, email, phone, city, state, gender, age, signup_date, is_active])
        customers.append(i)

# Introduce a few intentional data quality issues for the cleaning phase to fix
# (missing phone, duplicate-looking row) -- handled later in ETL/cleaning step.

# ---------- ORDERS + ORDER_ITEMS ----------
statuses = ["delivered","delivered","delivered","shipped","processing","pending","cancelled"]
payment_methods = ["Credit Card","Debit Card","UPI","Net Banking","Cash on Delivery"]

N_ORDERS = 220
orders_rows = []
items_rows = []
item_id = 1

with open(os.path.join(OUT_DIR, "orders.csv"), "w", newline="", encoding="utf-8") as fo, \
     open(os.path.join(OUT_DIR, "order_items.csv"), "w", newline="", encoding="utf-8") as fi:

    wo = csv.writer(fo)
    wi = csv.writer(fi)
    wo.writerow(["order_id","customer_id","order_date","status","total_amount",
                 "discount_amount","shipping_city","shipping_state","payment_method"])
    wi.writerow(["item_id","order_id","product_id","quantity","unit_price","discount_pct"])

    for order_id in range(1, N_ORDERS + 1):
        cust_id = random.choice(customers)
        order_date = datetime(2023,1,1) + timedelta(days=random.randint(0, 545),
                                                      hours=random.randint(0,23))
        status = random.choice(statuses)
        n_items = random.randint(1, 4)
        chosen_products = random.sample(products, n_items)

        order_total = 0
        for prod in chosen_products:
            qty = random.randint(1, 3)
            unit_price = prod["unit_price"]
            discount_pct = random.choice([0, 0, 0, 5, 10, 15])
            line_total = qty * unit_price * (1 - discount_pct/100)
            order_total += line_total
            wi.writerow([item_id, order_id, prod["product_id"], qty, unit_price, discount_pct])
            item_id += 1

        discount_amount = round(order_total * random.choice([0, 0, 0.05, 0.1]), 2)
        total_amount = round(order_total - discount_amount, 2)
        city, state = random.choice(cities_states)

        wo.writerow([order_id, cust_id, order_date.strftime("%Y-%m-%d %H:%M:%S"), status,
                     total_amount, discount_amount, city, state, random.choice(payment_methods)])

print("Sample data generated in:", os.path.abspath(OUT_DIR))
print(f"Categories: {len(categories)} | Products: {pid-1} | Customers: {N_CUSTOMERS} | Orders: {N_ORDERS} | Order items: {item_id-1}")

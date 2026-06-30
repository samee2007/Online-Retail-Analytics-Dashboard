"""
app.py
Streamlit dashboard for Online Retail Analytics.
Run with: streamlit run app.py
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from config import DB_URI

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide", page_icon="📊")

engine = create_engine(DB_URI)


@st.cache_data(ttl=300)
def run_query(sql, params=None):
    return pd.read_sql(sql, engine, params=params)


# ────────────────────────────────────────────────────────────
# SIDEBAR — FILTERS
# ────────────────────────────────────────────────────────────
st.sidebar.title("🔎 Filters")

date_bounds = run_query("SELECT MIN(order_date)::date AS min_d, MAX(order_date)::date AS max_d FROM orders")
min_date, max_date = date_bounds.loc[0, "min_d"], date_bounds.loc[0, "max_d"]

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

categories_df = run_query("SELECT category_name FROM categories ORDER BY category_name")
selected_categories = st.sidebar.multiselect(
    "Category", options=categories_df["category_name"].tolist(),
    default=categories_df["category_name"].tolist()
)

status_df = run_query("SELECT DISTINCT status FROM orders ORDER BY status")
selected_statuses = st.sidebar.multiselect(
    "Order status", options=status_df["status"].tolist(),
    default=[s for s in status_df["status"].tolist() if s != "cancelled"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Data refreshes every 5 minutes (cached).")

# Build dynamic WHERE clause safely using parameters
cat_filter = "(" + ",".join([f"'{c}'" for c in selected_categories]) + ")" if selected_categories else "('__none__')"
status_filter = "(" + ",".join([f"'{s}'" for s in selected_statuses]) + ")" if selected_statuses else "('__none__')"

# ────────────────────────────────────────────────────────────
# HEADER
# ────────────────────────────────────────────────────────────
st.title("📊 Online Retail Analytics Dashboard")
st.caption("Connected live to PostgreSQL · Internship Project")

# ────────────────────────────────────────────────────────────
# KPI CARDS
# ────────────────────────────────────────────────────────────
kpi_sql = f"""
SELECT
    COUNT(DISTINCT o.order_id)        AS total_orders,
    COUNT(DISTINCT o.customer_id)     AS unique_customers,
    COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)), 0) AS revenue,
    COALESCE(AVG(o.total_amount), 0)  AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p      ON oi.product_id = p.product_id
JOIN categories c    ON p.category_id = c.category_id
WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
  AND c.category_name IN {cat_filter}
  AND o.status IN {status_filter}
"""
kpis = run_query(kpi_sql).iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{kpis['revenue']:,.0f}")
col2.metric("Total Orders", f"{int(kpis['total_orders']):,}")
col3.metric("Unique Customers", f"{int(kpis['unique_customers']):,}")
col4.metric("Avg Order Value", f"₹{kpis['avg_order_value']:,.0f}")

st.markdown("---")

# ────────────────────────────────────────────────────────────
# TIME SERIES — REVENUE TREND
# ────────────────────────────────────────────────────────────
st.subheader("📈 Revenue Trend Over Time")

trend_sql = f"""
SELECT
    o.order_date::date AS order_day,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p      ON oi.product_id = p.product_id
JOIN categories c    ON p.category_id = c.category_id
WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
  AND c.category_name IN {cat_filter}
  AND o.status IN {status_filter}
GROUP BY o.order_date::date
ORDER BY order_day
"""
trend_df = run_query(trend_sql)

if not trend_df.empty:
    trend_df["order_day"] = pd.to_datetime(trend_df["order_day"])
    trend_df["revenue_7d_avg"] = trend_df["revenue"].rolling(7, min_periods=1).mean()

    fig = px.line(trend_df, x="order_day", y=["revenue", "revenue_7d_avg"],
                  labels={"order_day": "Date", "value": "Revenue (₹)", "variable": ""},
                  title=None)
    fig.update_layout(legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for the selected filters.")

st.markdown("---")

# ────────────────────────────────────────────────────────────
# CATEGORY + PRODUCT CHARTS
# ────────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("🗂️ Revenue by Category")
    cat_sql = f"""
    SELECT c.category_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p      ON oi.product_id = p.product_id
    JOIN categories c    ON p.category_id = c.category_id
    WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
      AND c.category_name IN {cat_filter}
      AND o.status IN {status_filter}
    GROUP BY c.category_name
    ORDER BY revenue DESC
    """
    cat_df = run_query(cat_sql)
    if not cat_df.empty:
        fig2 = px.bar(cat_df, x="category_name", y="revenue",
                       labels={"category_name": "Category", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader("🏆 Top 10 Products")
    top_prod_sql = f"""
    SELECT p.product_name,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p      ON oi.product_id = p.product_id
    JOIN categories c    ON p.category_id = c.category_id
    WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
      AND c.category_name IN {cat_filter}
      AND o.status IN {status_filter}
    GROUP BY p.product_name
    ORDER BY revenue DESC
    LIMIT 10
    """
    top_prod_df = run_query(top_prod_sql)
    if not top_prod_df.empty:
        fig3 = px.bar(top_prod_df, x="revenue", y="product_name", orientation="h",
                       labels={"product_name": "Product", "revenue": "Revenue (₹)"})
        fig3.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ────────────────────────────────────────────────────────────
# CUSTOMER SEGMENTATION + GEOGRAPHY
# ────────────────────────────────────────────────────────────
left2, right2 = st.columns(2)

with left2:
    st.subheader("👥 Revenue by City")
    city_sql = f"""
    SELECT o.shipping_city AS city,
           SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p      ON oi.product_id = p.product_id
    JOIN categories c    ON p.category_id = c.category_id
    WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
      AND c.category_name IN {cat_filter}
      AND o.status IN {status_filter}
    GROUP BY o.shipping_city
    ORDER BY revenue DESC
    LIMIT 10
    """
    city_df = run_query(city_sql)
    if not city_df.empty:
        fig4 = px.bar(city_df, x="city", y="revenue",
                       labels={"city": "City", "revenue": "Revenue (₹)"})
        st.plotly_chart(fig4, use_container_width=True)

with right2:
    st.subheader("🎯 Top 10 Customers (Lifetime Value)")
    cust_sql = f"""
    SELECT c.customer_name, c.city,
           SUM(o.total_amount) AS lifetime_value,
           COUNT(DISTINCT o.order_id) AS total_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    JOIN categories cat ON p.category_id = cat.category_id
    WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
      AND cat.category_name IN {cat_filter}
      AND o.status IN {status_filter}
    GROUP BY c.customer_name, c.city
    ORDER BY lifetime_value DESC
    LIMIT 10
    """
    cust_df = run_query(cust_sql)
    st.dataframe(cust_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ────────────────────────────────────────────────────────────
# DRILL-DOWN: ORDER STATUS BREAKDOWN
# ────────────────────────────────────────────────────────────
st.subheader("🔬 Drill-down: Orders by Status")
status_breakdown_sql = f"""
SELECT status, COUNT(*) AS order_count, SUM(total_amount) AS total_value
FROM orders
WHERE order_date::date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY status
ORDER BY order_count DESC
"""
status_df2 = run_query(status_breakdown_sql)

c1, c2 = st.columns([1, 2])
with c1:
    st.dataframe(status_df2, use_container_width=True, hide_index=True)
with c2:
    if not status_df2.empty:
        fig5 = px.pie(status_df2, names="status", values="order_count", hole=0.4)
        st.plotly_chart(fig5, use_container_width=True)

with st.expander("📋 View raw order-level data"):
    raw_sql = f"""
    SELECT o.order_id, c.customer_name, o.order_date, o.status,
           o.total_amount, o.shipping_city, o.payment_method
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_date::date BETWEEN '{start_date}' AND '{end_date}'
      AND o.status IN {status_filter}
    ORDER BY o.order_date DESC
    LIMIT 200
    """
    st.dataframe(run_query(raw_sql), use_container_width=True, hide_index=True)

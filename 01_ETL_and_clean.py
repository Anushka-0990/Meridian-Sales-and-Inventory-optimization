"""
ENGAGEMENT: Meridian Retail Corp - Sales & Inventory Optimization
Deliverable 01: Extract, Transform, Load (ETL) & Data Quality

Builds a clean, analysis-ready warehouse from the raw public "Superstore"
retail transactions dataset. Outputs:
  - data_clean/orders_clean.csv      (cleaned fact table)
  - data_clean/dim_product.csv       (product dimension w/ inventory keys)
  - data_clean/dim_geo.csv           (region/state dimension)
  - warehouse.db                     (SQLite star-schema warehouse)

Tools demonstrated: Python (pandas), SQL (SQLite) -- the ETL layer of a
consulting data/analytics engagement.
"""

import pandas as pd
import sqlite3
import os

RAW = "data_raw/superstore_raw.xlsx"
OUT_CLEAN = "data_clean/orders_clean.csv"
OUT_PROD  = "data_clean/dim_product.csv"
OUT_GEO   = "data_clean/dim_geo.csv"
DB        = "warehouse.db"

os.makedirs("data_clean", exist_ok=True)

print("="*70)
print("STEP 1 - EXTRACT")
print("="*70)
df = pd.read_excel(RAW)
df.columns = [c.strip() for c in df.columns]   # strip stray spaces
print(f"Raw rows : {len(df):,}   Raw columns: {df.shape[1]}")

# ----------------------------------------------------------------------------
print("\n" + "="*70)
print("STEP 2 - TRANSFORM / DATA QUALITY")
print("="*70)

# 2.1 Drop un-usable / helper columns
drop_cols = [c for c in ["Row ID", "ind1", "ind2"] if c in df.columns]
# drop any stray helper column beginning with 'Row' (e.g. messy import names)
drop_cols += [c for c in df.columns if str(c).strip().lower().startswith("row")]
df = df.drop(columns=drop_cols, errors="ignore")

# 2.2 Standardize dates
for col in ["Order Date", "Ship Date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# 2.3 Numeric coercion + reasonableness checks
for col in ["Sales", "Quantity", "Profit"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 2.4 Returns -> binary flag (business meaning: was the line-item returned?)
df["is_return"] = df["Returns"].fillna(0).astype(int)

# 2.5 Handle nulls
before = len(df)
df = df.dropna(subset=["Order ID", "Order Date", "Product ID", "Sales"])
print(f"Rows after dropping incomplete core records: {before:,} -> {len(df):,}")

# 2.6 Add engineered / calendar features
df["order_year"]  = df["Order Date"].dt.year
df["order_month"] = df["Order Date"].dt.month
df["order_quarter"] = df["Order Date"].dt.quarter
# Transit / fulfillment days (proxy for client supply-chain lead-time class)
df["fulfillment_days"] = (df["Ship Date"] - df["Order Date"]).dt.days

# 2.7 Gross margin % (profit as a share of sales), handle zero/negative
df["margin_pct"] = (df["Profit"] / df["Sales"]).replace([float("inf"), -float("inf")], float("nan"))

# 2.8 Standardise string fields for clean joins
for col in ["Country", "City", "State", "Region", "Category",
            "Sub-Category", "Segment", "Ship Mode", "Payment Mode"]:
    df[col] = df[col].astype(str).str.strip()

# 2.9 Logical de-duplication of order lines
n_dupes = df.duplicated(subset=["Order ID", "Product ID"]).sum()
df = df.drop_duplicates(subset=["Order ID", "Product ID"])
print(f"Duplicate order-lines removed: {n_dupes}")

# 2.10 Data quality summary table
print("\n--- Data quality summary ---")
print(f"Orders     : {df['Order ID'].nunique():,}")
print(f"Order lines: {len(df):,}")
print(f"Customers  : {df['Customer ID'].nunique():,}")
print(f"Products   : {df['Product ID'].nunique():,}")
print(f"Nulls left :\n{df.isna().sum()[df.isna().sum()>0].to_dict() or 'None'}")

# ----------------------------------------------------------------------------
print("\n" + "="*70)
print("STEP 3 - DIMENSIONS")
print("="*70)
# Product dimension: de-dup at product level; later enriched with inventory KPIs
dim_product = df[["Product ID", "Product Name", "Category",
                  "Sub-Category"]].drop_duplicates("Product ID").reset_index(drop=True)

# Geography dimension
dim_geo = df[["Region", "Country", "State", "City"]].drop_duplicates().reset_index(drop=True)

dim_product.to_csv(OUT_PROD, index=False)
dim_geo.to_csv(OUT_GEO, index=False)
print(f"dim_product: {dim_product.shape} -> {OUT_PROD}")
print(f"dim_geo    : {dim_geo.shape} -> {OUT_GEO}")

# Fact table = cleaned orders
orders = df[[c for c in df.columns if c != "Returns"]].copy()
orders.to_csv(OUT_CLEAN, index=False)
print(f"orders_clean: {orders.shape} -> {OUT_CLEAN}")

# snake_case copy for clean SQL identifier handling in the warehouse
def snake(s):
    s = s.lower().replace("-", "_").replace(" ", "_")
    return s
orders_db = orders.copy()
orders_db.columns = [snake(c) for c in orders.columns]
print("Warehouse fact columns:", orders_db.columns.tolist())

# ----------------------------------------------------------------------------
print("\n" + "="*70)
print("STEP 4 - LOAD into SQL data warehouse (SQLite star-schema)")
print("="*70)
if os.path.exists(DB):
    os.remove(DB)
conn = sqlite3.connect(DB)
orders_db.to_sql("fact_orders", conn, if_exists="replace", index=False)
# snake_case dims too
dp = dim_product.copy(); dp.columns = [snake(c) for c in dp.columns]
dg = dim_geo.copy();     dg.columns = [snake(c) for c in dg.columns]
dp.to_sql("dim_product", conn, if_exists="replace", index=False)
dg.to_sql("dim_geo", conn, if_exists="replace", index=False)

# Simple derived / aggregate tables analysts query often
def mart(df, keys, aggcols, name):
    g = df.groupby(keys, as_index=False)[aggcols].sum()
    g.columns = [c.lower().replace("-", "_").replace(" ", "_") for c in g.columns]
    g.to_sql(name, conn, if_exists="replace", index=False)

mart(orders, ["Region", "Category", "Sub-Category"],
     ["Quantity", "Sales", "Profit"], "mart_region_category")
mart(orders, ["order_year", "order_month", "Category"],
     ["Quantity", "Sales", "Profit"], "mart_monthly")
print("Warehouse tables:", [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()])
conn.close()
print("\nETL complete ✔  Clean files + warehouse.db written.")

"""
ENGAGEMENT: Meridian Retail Corp - Sales & Inventory Optimization
Deliverable 03: Analytical modeling (Python + scikit-learn)

Part A  - Demand forecasting  (per sub-category, next 12 months)
Part B  - ABC (value) x XYZ (volatility) inventory segmentation
Part C  - Inventory policy engine: safety stock, reorder point, max stock
Part D  - Slow-mover / dead-stock & returns-risk flagging
Part E  - Charts for the report

NOTE ON DATA: the core input is real public retail order data. True on-hand
stock/supplier lead-time files are not public here, so inventory "on-hand"
levels are modelled from demand & turnover assumptions -- stated transparently,
exactly as consultants present a model with stated assumptions.
"""

import pandas as pd, numpy as np, sqlite3, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

DB = "warehouse.db"
os.makedirs("outputs", exist_ok=True)
os.makedirs("images", exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "font.size": 9, "axes.grid": True,
                     "grid.alpha": .3, "axes.spines.top": False,
                     "axes.spines.right": False})

conn = sqlite3.connect(DB)
f = pd.read_sql_query("SELECT * FROM fact_orders", conn)
f["order_date"] = pd.to_datetime(f["order_date"])

SERVICE_LEVEL_Z = 1.65          # 95% service level (normal z-score)
REPLENISH_LEAD_DAYS = 7         # modelled replenishment lead-time assumption

# ============================================================================
print("="*70); print("PART A - DEMAND FORECASTING (12-mo ahead)"); print("="*70)
#=============================================================================
# Monthly units & revenue by sub-category, in chronological order
f["month"] = f.order_date.dt.to_period("M").astype(str)
sub = f.groupby(["month", "sub_category"], as_index=False) \
       .agg(units=("quantity","sum"), revenue=("sales","sum"))
sub = sub.sort_values("month")

def damp(trend, mean_hist):
    return np.clip(trend, mean_hist*0.3, mean_hist*2.5)

forecasts = []
for sc, g in sub.groupby("sub_category"):
    g = g.sort_values("month").reset_index(drop=True)
    g["t"] = np.arange(len(g))
    row = {"sub_category": sc}
    for target in ["units","revenue"]:
        y = g[target].values.astype(float)
        mean_hist = y.mean()
        # Full-data fit for the 12-mo horizon forecast
        model = LinearRegression().fit(g[["t"]], y)
        Xf = np.arange(len(g), len(g)+12).reshape(-1,1)
        trend = damp(model.predict(Xf), mean_hist)
        row[f"{target}_forecast_total_12m"] = trend.sum()
        row[f"{target}_forecast_monthly_avg"] = trend.mean()
        # Holdout accuracy: train on all-but-last-6, score those 6
        if len(y) >= 12:
            n_tr = len(y) - 6
            m2 = LinearRegression().fit(g[["t"]][:n_tr], y[:n_tr])
            pred = m2.predict(g[["t"]][n_tr:])
            act = y[n_tr:]
            row[f"{target}_holdout_mape_pct"] = float(
                np.mean(np.abs(act - pred)/(act+1e-9))*100)
    forecasts.append(row)
fc = pd.DataFrame(forecasts)
fc = fc.merge(sub.groupby("sub_category", as_index=False).agg(
    hist_units=("units","sum"), hist_revenue=("revenue","sum"),
    avg_monthly_units=("units","mean")), on="sub_category")
fc.to_csv("outputs/forecast_demand.csv", index=False)
print("Forecast written -> outputs/forecast_demand.csv")
print(fc.round(0).sort_values("units_forecast_total_12m", ascending=False).head(6).to_string(index=False))

# Plot: actual vs forecast for the 3 biggest sub-categories
top3 = sub.groupby("sub_category").revenue.sum().sort_values(ascending=False).head(3).index
fig, axes = plt.subplots(3,1, figsize=(8,9), sharex=False)
for ax, sc in zip(axes, top3):
    g = sub[sub.sub_category==sc].sort_values("month")
    ym = [pd.Period(x).strftime("%y-%m") for x in g.month]
    ax.plot(range(len(g)), g.revenue, marker="o", lw=1.6, color="#0b5fa5", label="Actual")
    ax.set_xticks(range(len(g))); ax.set_xticklabels(ym, rotation=90)
    trend_avg = fc[fc.sub_category==sc].revenue_forecast_monthly_avg.values[0]
    start = len(g)
    ax.axvline(start-0.5, color="grey", ls=":", lw=1)
    ax.plot(range(start, start+12), [trend_avg]*12, ls="--", color="#e07b00",
            label="Forecast (avg)")
    ax.set_title(f"{sc} - monthly revenue (USD)", fontweight="bold")
    ax.legend(loc="upper left", frameon=False)
plt.tight_layout(); plt.savefig("images/forecast_demand.png", bbox_inches="tight")
plt.close(); print("chart -> images/forecast_demand.png")

# ============================================================================
print("\n"+"="*70); print("PART B - ABC x XYZ INVENTORY SEGMENTATION"); print("="*70)
#=============================================================================
# Product-level metrics
prod = f.groupby("product_id", as_index=False).agg(
    product_name=("product_name","first"), category=("category","first"),
    sub_category=("sub_category","first"),
    units=("quantity","sum"), revenue=("sales","sum"), profit=("profit","sum"),
    returns=("is_return","sum"), n_orders=("order_id","nunique"))

# XYZ volatility: CV of monthly units (need per-product monthly grid)
pm = f.groupby(["month", "product_id"], as_index=False) \
      .agg(units=("quantity","sum"))
prod["monthly_std"] = prod.product_id.map(pm.groupby("product_id").units.std())
prod["monthly_mean"] = prod.product_id.map(pm.groupby("product_id").units.mean())
prod["cv"] = (prod.monthly_std / prod.monthly_mean.replace(0,np.nan)).fillna(9)

# --- ABC by profit contribution (Pareto) ---
p = prod.sort_values("profit", ascending=False).reset_index(drop=True)
total_profit = p.profit.sum()
p["cum_profit_share"] = p.profit.cumsum() / total_profit
def abc(c):
    if c <= .80: return "A"
    if c <= .95: return "B"
    return "C"
p["abc_class"] = p.cum_profit_share.apply(abc)

# --- XYZ by demand volatility ---
def xyz(cv):
    if cv <= 0.5:  return "X"
    if cv <= 1.0:  return "Y"
    return "Z"
p["xyz_class"] = p.cv.apply(xyz)

p.to_csv("outputs/abc_xyz_products.csv", index=False)
print("Product segmentation written -> outputs/abc_xyz_products.csv")

# Policy matrix mapping (classic supply-chain heuristic)
policy = {
    ("A","X"): "CORE - high availability, tight monitoring",
    ("A","Y"): "MANAGE - replenish on forecast",
    ("B","X"): "STANDARD - normal replenishment",
    ("B","Y"): "WATCH - moderate safety stock",
    ("A","Z"): "BALANCE - protect availability, cap stock",
    ("B","Z"): "REDUCE - cut stock, watch variability",
    ("C","X"): "LEAN - keep minimal base stock",
    ("C","Y"): "LEAN - order to demand",
    ("C","Z"): "OBSOLETE-RISK - minimise/phase out",
}
p["inventory_policy"] = p.apply(
    lambda r: policy.get((r.abc_class, r.xyz_class), ""), axis=1)
matrix = p.groupby(["abc_class","xyz_class"]).size().unstack(fill_value=0)
print("\nABC x XYZ product-count matrix:\n", matrix)
print("\nPolicy recommendation summary:\n", p.inventory_policy.value_counts())

# Chart: ABC-XYZ matrix (bubble counts)
fig, ax = plt.subplots(figsize=(6.5,4.2))
order_abc = ["A","B","C"]; order_xyz = ["X","Y","Z"]
def mat_val(a, x):
    if a not in matrix.index or x not in matrix.columns:
        return 0
    return int(matrix.at[a, x])
data = np.array([[mat_val(a, x) for x in order_xyz] for a in order_abc], dtype=float)
im = ax.imshow(data, cmap="YlOrRd")
ax.set_xticks(range(3)); ax.set_xticklabels(order_xyz)
ax.set_yticks(range(3)); ax.set_yticklabels(order_abc)
for i in range(3):
    for j in range(3):
        ax.text(j,i, int(data[i,j]), ha="center", va="center",
                color="white" if data[i,j] > data.max()/2 else "black", fontweight="bold")
ax.set_title("ABC (profit) x XYZ (volatility) product matrix", fontweight="bold")
ax.set_xlabel("XYZ demand volatility"); ax.set_ylabel("ABC value class")
plt.tight_layout(); plt.savefig("images/abc_xyz_matrix.png", bbox_inches="tight")
plt.close(); print("chart -> images/abc_xyz_matrix.png")

# ============================================================================
print("\n"+"="*70); print("PART C - INVENTORY POLICY ENGINE"); print("="*70)
#=============================================================================
# Use average order-to-delivery as the modelled replenishment lead-time proxy
avg_fulfill = f.fulfillment_days.mean()
lead_days = REPLENISH_LEAD_DAYS
p["avg_monthly_demand"] = p.units / 12.0
p["daily_demand"] = p.units / 365.0
p["demand_std"] = p.monthly_std.fillna(p.avg_monthly_demand)  # sigma/month
p["safety_stock"] = np.ceil(SERVICE_LEVEL_Z * p.demand_std * np.sqrt(lead_days/30.4))
p["reorder_point"] = np.ceil(p.daily_demand * lead_days + p.safety_stock)
p["recommended_max_stock"] = np.ceil(p.reorder_point + p.avg_monthly_demand)
p["stock_action"] = np.where(
    p.abc_class.isin(["A","B"]) & p.xyz_class.isin(["X","Y"]),
    "STOCK-UP (high value, stable demand)",
    np.where(p.inventory_policy.str.startswith("OBSOLETE"),
             "REVIEW / PHASE-OUT", "MINIMISE STOCK"))
cols = ["product_id","product_name","category","sub_category","units","revenue",
        "profit","abc_class","xyz_class","inventory_policy","avg_monthly_demand",
        "safety_stock","reorder_point","recommended_max_stock","stock_action"]
inv = p[cols].sort_values("abc_class")
inv.to_csv("outputs/inventory_policy.csv", index=False)
print("Inventory policy written -> outputs/inventory_policy.csv "
      f"(service level 95%, modelled lead {lead_days}d, avg fulfillment {avg_fulfill:.1f}d)")

# ============================================================================
print("\n"+"="*70); print("PART D - SLOW MOVER / DEAD STOCK & RETURNS RISK"); print("="*70)
#=============================================================================
dead = p[p.abc_class=="C"].sort_values("units")
deadstock = dead[dead.units <= 2]
slow = p[(p.units > 2) & (p.units <= p.units.quantile(.25))].sort_values("units")
p["returns_rate_pct"] = p.returns / p.n_orders * 100
high_return = p[p.returns_rate_pct >= 15].sort_values("returns_rate_pct", ascending=False)
print(f"Dead-stock candidates (<=2 units over 2 yrs): {len(deadstock)}")
print(f"Slow-movers (bottom quartile units): {len(slow)}")
print(f"High-return-risk products (>=15% line return rate): {len(high_return)}")

# Combined risk register -> genuine exception list (actionable, not the whole tail)
p["risk_flag"] = ""
p.loc[deadstock.index, "risk_flag"] += "DEAD-STOCK;"
p.loc[high_return.index, "risk_flag"] += "HIGH-RETURN;"
# obsolete/phase-out = C-class with high volatility (Z)
p.loc[(p.abc_class=="C") & (p.xyz_class=="Z"), "risk_flag"] += "OBSOLETE-RISK;"
# chronic loss-makers (negative profit AND non-trivial volume)
p.loc[(p.profit < 0) & (p.units >= 5), "risk_flag"] += "LOSS-MAKING;"
risk = p[p.risk_flag!=""][["product_id","product_name","sub_category","units",
        "revenue","profit","returns_rate_pct","risk_flag","stock_action"]]
risk = risk.sort_values("profit")
risk.to_csv("outputs/risk_register.csv", index=False)
print("Risk register written -> outputs/risk_register.csv  "
      f"({len(risk)} genuinely flagged exception SKUs)")
print(risk.risk_flag.str.replace(";","").value_counts().to_dict())

# Charts: slow movers don't print individually (crowded). Returns by category:
rb = f.groupby("category").agg(lines=("is_return","size"),
    returns=("is_return","sum")).assign(rr=lambda d: d.returns/d.lines*100).sort_values("rr")
fig, ax = plt.subplots(figsize=(6.5,3.6))
ax.bar(rb.index, rb.rr, color=["#0b5fa5","#e07b00","#7a1f1f"])
for i,v in enumerate(rb.rr): ax.text(i, v+.1, f"{v:.1f}%", ha="center", fontweight="bold")
ax.set_ylabel("Return rate (%)"); ax.set_title("Return rate by category", fontweight="bold")
plt.tight_layout(); plt.savefig("images/return_by_category.png", bbox_inches="tight")
plt.close(); print("chart -> images/return_by_category.png")
conn.close()
print("\nModelling complete ✔  Outputs written to /outputs and /images")

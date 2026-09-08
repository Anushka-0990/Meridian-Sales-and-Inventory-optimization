<div align="center">

# Meridian Retail Corp — Sales & Inventory Optimization

### End-to-end retail analytics engagement · **Python · SQL · Excel · Power BI**

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoftexcel&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![status](https://img.shields.io/badge/status-reproducible-success)

A consulting-style analytics project demonstrating the full **Python + SQL +
Power BI + Excel** stack, built for the kind of retail client work done at
**KPMG (Digital Lighthouse)** and **Deloitte**.

**Data:** real public retail order dataset — **5,901 order-lines · 1,755 SKUs ·
2019–2020 · 4 regions**.

</div>

---

## 📌 Business problem

> Revenue is growing, but **margin leaks** through returns, dead stock and a
> long tail of loss-making SKUs.
> *Which regions/categories should we defend? Which SKUs should we cut? How much
> should we stock — and of what?*

---

## 🧱 What I did, layer by layer

| Layer | Deliverable |
|---|---|
| **SQL** | Clean data → build star-schema `warehouse.db` → run **9 business queries** (regional P&L, sub-category profit, returns, monthly trends) |
| **Python** | **12-month demand forecast** · **ABC×XYZ** inventory segmentation · **safety-stock / reorder-point** policy engine · exception **risk register** |
| **Excel** | Client-ready data pack: KPI cards + native charts (`retail_analytics_deliverable.xlsx`) |
| **Power BI** | Live executive dashboard build guide + DAX measures |

---

## 🔍 Key findings

- **West-region return rate is 9.9% vs 2.2% elsewhere** — yet the West is the most
  profitable region (13% margin). Strong signal of a *fulfilment/QA* issue, not the customer base.
- **307 SKUs are net loss-makers (−$52.8K)** and **92 SKUs are effectively dead stock** (~$15.8K value).
- **Copiers carry a 71.6% margin** while several Machines/Tables SKUs lose value per unit → "double down / cut loose" per sub-category.
- **ABC×XYZ policy matrix** guides stock depth: 48 CORE SKUs to protect, 321 volatile low-value SKUs to phase out.

> **Estimated margin release from recommended actions: ~$50–70K / year.**

---

## 📊 Visuals

![ABC x XYZ inventory matrix](images/abc_xyz_matrix.png)
![Demand forecast](images/forecast_demand.png)
![Returns by category](images/return_by_category.png)

---

## 📂 Project structure

```
meridian-retail-analytics/
├─ 01_ETL_and_clean.py           # ETL + data quality -> warehouse.db
├─ 02_business_SQL_analysis.sql  # 9 business queries (analyst SQL)
├─ 02_run_sql_analysis.py        # executes the .sql file
├─ 03_model_inventory.py         # forecast + ABC/XYZ + inventory policy engine
├─ 04_build_excel_deliverable.py # client Excel workbook (openpyxl)
├─ run_all.sh                    # one-command reproducible pipeline
├─ data_raw/                     # real public retail source data
├─ data_clean/                   # cleaned fact + dimension tables
├─ outputs/                      # sql results, forecast, policy, risk register
├─ images/                       # charts rendered in this README
├─ reports/Executive_Insight_Report.md
├─ POWERBI_DASHBOARD_GUIDE.md    # build the live Power BI dashboard
├─ warehouse.db                  # SQLite star-schema warehouse
├─ retail_analytics_deliverable.xlsx
├─ requirements.txt
└─ .github/workflows/ci.yml      # auto-runs the pipeline on every push
```

---

## ▶️ Run it yourself

```bash
pip install -r requirements.txt
bash run_all.sh
```

…or run the four Python files in order:

```bash
python3 01_ETL_and_clean.py
python3 02_run_sql_analysis.py
python3 03_model_inventory.py
python3 04_build_excel_deliverable.py
```

Outputs land in `outputs/`, `images/`, and `retail_analytics_deliverable.xlsx`.
A green ✓ in the Actions tab confirms the pipeline runs end-to-end on GitHub's servers.

---

## 🧠 Methodology & assumptions (disclosed)

Order transactions come from a public retail dataset. **On-hand stock and supplier
lead-times are not in the public data**, so inventory levels are **modelled** from
demand at a stated **95% service level** and **7-day lead-time** — the standard way
a consultant sets up a model before ERP integration. All assumptions are stated in
the Executive Insight Report.

**Methods:** linear-trend demand forecast with holdout MAPE · ABC by profit Pareto ·
XYZ by coefficient-of-variation of monthly demand · safety stock = `Z·σ·√(lead time)`.

---

## 🛠️ Tools

Python (pandas · scikit-learn · matplotlib · openpyxl) · SQL (SQLite) · Excel · Power BI DAX

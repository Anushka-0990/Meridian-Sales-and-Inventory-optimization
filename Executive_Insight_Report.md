# MERIDIAN RETAIL CORP
## Sales & Inventory Optimization — Analytics Insight Report

*Consulting engagement · Prepared for management review · Data: 2019–2020 (public retail order dataset, 5,901 orders / 1,755 SKUs)*

---

## 1. Executive summary

Meridian Retail's analytics review of **$1.56M revenue / $174K profit (11.2% net margin)** across four regions exposes a classic retail paradox: **the company's best-performing regions and categories carry hidden leakage** — in returns, in dead stock, and in a long tail of loss-making SKUs that quietly erode gross margin.

Three actions, in priority order, can release an estimated **$50–70K of annualized margin**:

1. **Fix West-region returns (9.9% vs. 2.2% elsewhere).** Returns are roughly **4× higher in the West** despite it being the *most profitable* region (13% margin). Even a halving of West returns lifts group margin measurably and cuts reverse-logistics cost.
2. **Rationalize the long tail.** 307 SKUs are net loss-makers (≈ **$52.8K** of cumulative loss) and 92 SKUs are effectively dead stock. Range pruning + a C-Z (low-value, high-volatility) phase-out releases capital tied up in inventory.
3. **Protect the margin engine.** Copiers earn a **71.6% margin** while several Machines and Tables SKUs lose 100%+ of their value per unit — a clear "double down / cut loose" signal per sub-category.

---

## 2. Where the money is made & lost

### 2.1 Regional P&L

| Region | Revenue | Profit | Margin % | Return rate % |
|---|---|---|---|---|
| **West** | $522K | $67.8K | **13.0%** | **9.9%** ⚠️ |
| East | $450K | $52.9K | 11.7% | 2.8% |
| South | $251K | $26.4K | 10.5% | 2.2% |
| Central | $341K | $27.5K | 8.0% | 2.2% |

**Insight:** The West is the profit leader *and* the returns hotspot. This points to a fulfilment/quality issue in the West distribution node, not to the customer base — the same SKUs that return cleanly in other regions come back at ~10% in the West.

### 2.2 Category & sub-category profitability

| Sub-category | Category | Profit | Margin % | Read |
|---|---|---|---|---|
| Copiers | Technology | $42.8K | **71.6%** | Margin engine — protect & push |
| Accessories | Technology | $25.3K | 20.7% | Strong |
| Phones | Technology | $22.3K | 11.3% | High volume |
| Paper | Office Supplies | $21.1K | 21.2% | Strong |
| Binders | Office Supplies | $17.9K | 10.2% | High volume |
| *Tables* | *Furniture* | *(see §4)* | *negative* | *Range risk* |
| *Machines* | *Technology* | *(see §4)* | *negative* | *Range risk* |

**Insight:** Technology sub-categories dominate profit. **Furniture is the weak leg** — Tables and Bookcases appear frequently in the loss-maker and dead-stock lists.

### 2.3 Segment & channel view
- **Consumer** is the largest profit pool ($81K), but **Home Office carries the best margin (11.9%)** with the fewest customers — an underserved, higher-quality segment to grow.
- **COD drives the most revenue ($667K)** — worth reviewing cash-cycle and return risk per channel.

---

## 3. Demand forecast (12-month)

Using a linear-trend model per sub-category (with a last-6-month holdout for accuracy), the top forward demand categories are:

| Sub-category | Forecast 12-mo revenue | Holdout MAPE |
|---|---|---|
| Binders | ~$215K | 42% |
| Phones | ~$179K | 26% |
| Accessories | ~$134K | 23% |
| Paper | ~$121K | 31% |
| Furniture/Furnishings | ~$111K | 39% |

**Use:** forecast drives the safety-stock and reorder-point engine (§4), so volatile but high-value SKUs (high XYZ) get protected availability while stable high-value SKUs (AX/BX) can carry leaner stock without stock-out risk.

*Limitation disclosed: holdout MAPE 23–42% reflects the spiky monthly demand in the public dataset; a production build would add seasonality (holiday peaks are visible in Nov–Dec) and promotion calendars.*

---

## 4. Inventory policy engine (ABC × XYZ)

SKUs are segmented by **profit contribution (ABC/Pareto)** and **demand volatility (XYZ)**:

| | X (stable) | Y (moderate) | Z (volatile) |
|---|---|---|---|
| **A** (top 80% profit) | 48 — **CORE**: high availability | 58 — **MANAGE**: forecast-driven | 10 — **BALANCE**: cap stock |
| **B** (next 15%) | 40 — STANDARD | 38 — WATCH | 4 — REDUCE |
| **C** (tail 5%) | 690 — LEAN: minimal base | 546 — LEAN: order to demand | 321 — **PHASE-OUT** |

**Policy outputs per SKU** (at 95% service level, modelled 7-day lead time):
`safety stock`, `reorder point`, and `recommended max stock` are computed for the A/B core SKUs in the `Inventory Policy` worksheet.

**Exception register (735 SKUs)** flagged for real action:
- **307 loss-making SKUs** (cumulative −$52.8K) → reprice or delist
- **92 dead-stock SKUs** (≤2 units in 2 yrs, ~$15.8K of value) → clearance/phase-out
- **174 high-return SKUs** (≥15% line return rate) → QA + description accuracy

---

## 5. Recommended action plan (90 days)

| # | Action | Owner | Target impact |
|---|---|---|---|
| 1 | West-region returns deep-dive (per SKU, per shipment node) | Supply chain + QA | Recover est. 3–4 pts margin in West |
| 2 | Delist/clear 307 loss-makers + 92 dead-stock SKUs | Buying team | Release ~$50–70K margin & working capital |
| 3 | Double down on Copiers/Accessories; review Tables & Machines range | Category mgmt | Margin mix shift to >15% |
| 4 | Apply AX/BX lean-stocking, A/B Z balancing from policy engine | Inventory planner | Cut stock-outs & excess stock |
| 5 | Grow Home Office segment (highest margin, fewest customers) | Marketing | Incremental high-margin revenue |

---

## 6. Methodology & assumptions (disclosed, consulting-standard)

1. **Data:** public retail "Superstore" order dataset (5,901 order-lines, 2019–2020). Cleaned for nulls, date coercion, duplicate order-lines, and engineered features (margin %, fulfilment days, return flag, calendar fields) in `01_ETL_and_clean.py`.
2. **Warehouse:** SQLite star-schema (`warehouse.db`) with `fact_orders`, `dim_product`, `dim_geo`, plus analyst `mart_*` tables.
3. **SQL:** 9 business queries (`02_business_SQL_analysis.sql`) reproduce every figure above.
4. **Modelling:** linear-trend demand forecast with holdout MAPE; ABC by profit Pareto; XYZ by coefficient of variation of monthly units; safety stock = `Z × σ_demand × √(lead_time)` at 95% service level (Z=1.65).
5. **Key assumption:** on-hand stock & supplier lead-times are **not part of the public dataset**, so inventory levels and lead time are *modelled from demand & a stated 7-day replenishment assumption*. This is stated so results are interpretable — and in a real client build these would be replaced by live ERP inputs.
6. **Reproducible end-to-end:** `01 → 02 → 03 → 04` in the project root regenerate every CSV, the SQL results, the model, the charts, and the Excel deliverable.

---

### Deliverables produced
- `warehouse.db` — star-schema data warehouse (SQL)
- `outputs/sql_*.csv` — results of the 9 SQL business queries
- `outputs/forecast_demand.csv`, `inventory_policy.csv`, `abc_xyz_products.csv`, `risk_register.csv`
- `retail_analytics_deliverable.xlsx` — client Excel data pack w/ native charts & KPIs
- `images/*.png` — forecast, ABC-XYZ matrix, returns-by-category charts
- `POWERBI_DASHBOARD_GUIDE.md` — import steps + DAX to build the live dashboard

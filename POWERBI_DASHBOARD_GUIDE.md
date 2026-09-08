# Building the Power BI Dashboard for Meridian Retail

> The `.pbix` itself is authored in **Power BI Desktop** (free, Windows). This
> guide gives you the exact model, import steps and DAX so you can build the
> live executive dashboard in ~15 minutes and demo it in your interview.

## 1. Create a clean semantic model (the "Data Model")

Open **Power BI Desktop → Get Data → Folder/CSV** and import these three tables
(pre-generated in this project) and set up relationships:

| Table (Power BI name) | Source file | Role |
|---|---|---|
| `Orders` | `data_clean/orders_clean.csv` | Fact (grain = order line) |
| `Products` | `data_clean/dim_product.csv` | Dimension (Category / Sub-Category) |
| `Inventory` | `outputs/inventory_policy.csv` | Dimension (ABC-XYZ, safety stock, reorder point) |

**Relationships (Model view):**
- `Products[Product ID]` 1→* `Orders[Product ID]`
- `Inventory[product_id]` 1→* `Orders[Product ID]`

Mark `Orders[Order Date]` as a **Date** column. Confirm `Sales`, `Quantity`,
`Profit` are whole/decimal numbers.

## 2. DAX measures (New Measure — paste these)

```
Revenue      = SUM('Orders'[Sales])
Profit       = SUM('Orders'[Profit])
Gross Margin = DIVIDE([Profit], [Revenue])
Return Rate  = DIVIDE(SUM('Orders'[is_return]), COUNTROWS('Orders')) * 100
AOV          = DIVIDE([Revenue], DISTINCTCOUNT('Orders'[Order ID]))
```

> Column names above match the CSV headers exactly (e.g. `Order ID`, `Product
> ID`, `Sales`, `is_return`). Let DAX **autocomplete** verify each reference.

## 3. Build the report pages

**Page 1 — Executive Overview**
- 4 KPI cards: Revenue, Gross Margin %, Return Rate, AOV
- Bar chart: **Revenue & Profit by Region** (from `Orders[Region]`)
- Column chart: **Monthly Revenue & Profit** (Date axis)

**Page 2 — Category & Product**
- Bar chart: **Profit by Sub-Category**
- Table/matrix: Sub-Category × margin %, return rate
- Treemap: **Revenue by Category**

**Page 3 — Inventory & Risk**
- Slicer: **ABC class** and **XYZ class**
- Table: Product, Inventory Policy, Safety Stock, Reorder Point
- Matrix: **ABC × XYZ** product count (rows = ABC, columns = XYZ)
- Chart: Return Rate by Category

## 4. Interview talking points (what you demo)
1. "Data was loaded into a **star-schema model** with explicit relationships."
2. "The **Return Rate** measure exposes the West-region anomaly (9.9% vs 2.2%)."
3. "**ABC × XYZ** drives the inventory policy engine — I can filter to A/B/C and
   Z to show phase-out candidates."
4. "All measures are **DAX**, computed live from the model, so you can drill by
   region, category or month."

## Optional: push to the Power BI Service
Publish from Desktop → create a workspace → share the dashboard link. This shows
you can operate the full BI stack, not just report building.

-- ============================================================================
-- MERIDIAN RETAIL CORP  |  SQL Business Analysis
-- Runs against warehouse.db (SQLite star-schema built in 01_ETL_and_clean.py)
-- Each query answers a question a retail client stakeholder would ask.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- Q1. Executive KPI scorecard (fiscal 2019-2020)
-- ---------------------------------------------------------------------------
SELECT COUNT(DISTINCT Order_ID)                             AS orders,
       COUNT(*)                                             AS order_lines,
       ROUND(SUM(Sales),0)                                  AS revenue_usd,
       ROUND(SUM(Profit),0)                                 AS gross_profit_usd,
       ROUND(SUM(Profit)/SUM(Sales)*100,1)                  AS margin_pct,
       ROUND(SUM(CASE WHEN is_return=1 THEN 1 ELSE 0 END)
             *100.0/COUNT(*),1)                             AS return_rate_pct,
       ROUND(AVG(Sales),2)                                  AS avg_order_value
FROM fact_orders;

-- ---------------------------------------------------------------------------
-- Q2. Regional performance - where is money made / lost?
-- ---------------------------------------------------------------------------
SELECT Region,
       ROUND(SUM(Sales),0)      AS revenue,
       ROUND(SUM(Profit),0)     AS profit,
       ROUND(SUM(Profit)/SUM(Sales)*100,1) AS margin_pct,
       ROUND(SUM(CASE WHEN is_return=1 THEN 1 ELSE 0 END)
             *100.0/COUNT(*),1) AS return_rate_pct
FROM fact_orders
GROUP BY Region
ORDER BY profit DESC;

-- ---------------------------------------------------------------------------
-- Q3. Sub-category profitability - inventory heroes vs. loss-makers
-- ---------------------------------------------------------------------------
SELECT Sub_Category, Category,
       ROUND(SUM(Sales),0)  AS revenue,
       ROUND(SUM(Profit),0) AS profit,
       ROUND(SUM(Profit)/NULLIF(SUM(Sales),0)*100,1) AS margin_pct,
       SUM(Quantity)        AS units_sold
FROM fact_orders
GROUP BY Sub_Category, Category
ORDER BY profit DESC;

-- ---------------------------------------------------------------------------
-- Q4. Return rate by sub-category - a proxy for quality / inventory risk
-- ---------------------------------------------------------------------------
SELECT Sub_Category,
       COUNT(*) AS lines,
       ROUND(100.0*SUM(is_return)/COUNT(*),1) AS return_rate_pct
FROM fact_orders
GROUP BY Sub_Category
HAVING COUNT(*) > 20
ORDER BY return_rate_pct DESC;

-- ---------------------------------------------------------------------------
-- Q5. Segment value - which customer group drives profit
-- ---------------------------------------------------------------------------
SELECT Segment,
       ROUND(SUM(Sales),0)  AS revenue,
       ROUND(SUM(Profit),0) AS profit,
       ROUND(SUM(Profit)/SUM(Sales)*100,1) AS margin_pct,
       COUNT(DISTINCT Customer_ID) AS customers
FROM fact_orders
GROUP BY Segment
ORDER BY profit DESC;

-- ---------------------------------------------------------------------------
-- Q6. Monthly revenue trend (for demand forecasting / seasonal planning)
-- ---------------------------------------------------------------------------
SELECT order_year, order_month,
       ROUND(SUM(Sales),0) AS revenue,
       ROUND(SUM(Profit),0) AS profit
FROM fact_orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- ---------------------------------------------------------------------------
-- Q7. Top 10 profit products  &  Bottom 10 (to inform range rationalisation)
-- ---------------------------------------------------------------------------
SELECT Product_Name, Sub_Category,
       ROUND(SUM(Sales),0)  AS revenue,
       ROUND(SUM(Profit),0) AS profit
FROM fact_orders
GROUP BY Product_Name
ORDER BY profit DESC
LIMIT 10;

SELECT Product_Name, Sub_Category,
       ROUND(SUM(Sales),0)  AS revenue,
       ROUND(SUM(Profit),0) AS profit,
       ROUND(AVG(margin_pct),1) AS avg_margin_pct
FROM fact_orders
GROUP BY Product_Name
ORDER BY profit ASC
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Q8. Payment / channel mix - for trade-terms & channel strategy
-- ---------------------------------------------------------------------------
SELECT Payment_Mode,
       COUNT(*) AS orders,
       ROUND(SUM(Sales),0) AS revenue
FROM fact_orders
GROUP BY Payment_Mode
ORDER BY revenue DESC;

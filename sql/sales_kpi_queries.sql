-- Sales Analytics Dashboard - KPI SQL Queries

-- 1. Main business KPIs
SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales;


-- 2. Sales and profit by region
SELECT
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales
GROUP BY region
ORDER BY total_sales DESC;


-- 3. Sales and profit by category
SELECT
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales
GROUP BY category
ORDER BY total_sales DESC;


-- 4. Monthly sales and profit trend
SELECT
    order_year_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY order_year_month
ORDER BY order_year_month;


-- 5. Top 10 products by sales
SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY product_name, category, sub_category
ORDER BY total_sales DESC
LIMIT 10;


-- 6. Top 10 products by profit
SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY product_name, category, sub_category
ORDER BY total_profit DESC
LIMIT 10;


-- 7. Least profitable products
SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY product_name, category, sub_category
ORDER BY total_profit ASC
LIMIT 10;


-- 8. Sales and profit by customer segment
SELECT
    segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales
GROUP BY segment
ORDER BY total_sales DESC;


-- 9. Discount impact on profit
SELECT
    discount,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(*) AS number_of_order_lines,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales
GROUP BY discount
ORDER BY discount;


-- 10. State-level sales and profit
SELECT
    state,
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
FROM sales
GROUP BY state, region
ORDER BY total_sales DESC;

-- =====================================================
-- PRODUCT SALES & PROFITABILITY ANALYSIS
-- CTE + DENSE_RANK + PROFIT MARGIN
-- =====================================================

WITH product_summary AS (

    SELECT
        product_id,
        product_name,
        category,
        sub_category,

        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit,

        COUNT(DISTINCT order_id) AS total_orders

    FROM sales

    WHERE product_id IS NOT NULL

    GROUP BY
        product_id,
        product_name,
        category,
        sub_category
),

ranked_products AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY total_sales DESC
        ) AS sales_rank,

        DENSE_RANK() OVER (
            ORDER BY total_profit DESC
        ) AS profit_rank

    FROM product_summary
)

SELECT
    product_id,
    product_name,
    category,
    sub_category,

    ROUND(total_sales, 2) AS total_sales,
    ROUND(total_profit, 2) AS total_profit,

    total_orders,

    ROUND(
        100.0 * total_profit
        / NULLIF(total_sales, 0),
        2
    ) AS profit_margin_pct,

    sales_rank,
    profit_rank,


CASE
    WHEN ROUND(total_profit, 2) < 0
        THEN 'Loss-making'
    WHEN ROUND(total_profit, 2) = 0
        THEN 'Break-even'
    ELSE 'Profitable'
END AS profitability_status


FROM ranked_products

ORDER BY total_sales DESC, product_id

LIMIT 15;

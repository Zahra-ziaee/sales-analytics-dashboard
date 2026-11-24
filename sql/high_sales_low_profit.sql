
-- =====================================================
-- HIGH SALES, LOW PROFITABILITY ANALYSIS
-- CTE + NTILE + BUSINESS BENCHMARK
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

company_benchmark AS (

    SELECT
        100.0 * SUM(profit)
        / NULLIF(SUM(sales), 0)
        AS company_profit_margin_pct

    FROM sales
),

ranked_products AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY total_sales DESC
        ) AS sales_rank,

        NTILE(4) OVER (
            ORDER BY
                total_sales DESC,
                product_id,
                product_name
        ) AS sales_quartile

    FROM product_summary
)

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,

    ROUND(p.total_sales, 2) AS total_sales,
    ROUND(p.total_profit, 2) AS total_profit,

    ROUND(
        100.0 * p.total_profit
        / NULLIF(p.total_sales, 0),
        2
    ) AS profit_margin_pct,

    ROUND(
        b.company_profit_margin_pct,
        2
    ) AS company_profit_margin_pct,

    p.total_orders,
    p.sales_rank,
    p.sales_quartile,

    CASE
        WHEN ROUND(p.total_profit, 2) < 0
            THEN 'Loss-making'

        WHEN ROUND(p.total_profit, 2) = 0
            THEN 'Break-even'

        ELSE 'Below company margin'
    END AS business_flag

FROM ranked_products p

CROSS JOIN company_benchmark b

WHERE
    p.sales_quartile = 1

    AND (
        100.0 * p.total_profit
        / NULLIF(p.total_sales, 0)
    ) < b.company_profit_margin_pct


ORDER BY
    p.total_profit ASC,
    p.total_sales DESC

LIMIT 20;

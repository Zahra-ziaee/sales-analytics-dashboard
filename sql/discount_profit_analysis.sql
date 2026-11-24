
-- =====================================================
-- DISCOUNT & PROFITABILITY ANALYSIS
-- Top loss-making products in the highest sales quartile
-- =====================================================

WITH product_summary AS (

    SELECT
        product_id,
        product_name,
        category,
        sub_category,

        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit,

        COUNT(*) AS order_lines,

        ROUND(
            100.0 * AVG(discount),
            2
        ) AS avg_discount_pct,

        ROUND(
            100.0 * SUM(
                CASE WHEN discount > 0 THEN 1 ELSE 0 END
            ) / NULLIF(COUNT(discount), 0),
            2
        ) AS discounted_lines_pct,

        ROUND(
            SUM(
                CASE
                    WHEN discount > 0 THEN profit
                    ELSE 0
                END
            ),
            2
        ) AS discounted_lines_profit,

        ROUND(
            SUM(
                CASE
                    WHEN discount = 0 THEN profit
                    ELSE 0
                END
            ),
            2
        ) AS full_price_lines_profit

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

        NTILE(4) OVER (
            ORDER BY
                total_sales DESC,
                product_id,
                product_name
        ) AS sales_quartile

    FROM product_summary
)

SELECT
    product_name,

    ROUND(total_sales, 2) AS total_sales,
    ROUND(total_profit, 2) AS total_profit,

    order_lines,
    avg_discount_pct,
    discounted_lines_pct,

    discounted_lines_profit,
    full_price_lines_profit

FROM ranked_products

WHERE
    sales_quartile = 1
    AND ROUND(total_profit, 2) < 0

ORDER BY
    total_profit ASC

LIMIT 10;

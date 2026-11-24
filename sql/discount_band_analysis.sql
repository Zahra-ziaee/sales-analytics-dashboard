
-- =====================================================
-- DISCOUNT BAND PROFITABILITY ANALYSIS
-- CTE + CASE + AGGREGATION
-- =====================================================

WITH discount_groups AS (

    SELECT
        order_id,
        sales,
        profit,
        discount,

        CASE
            WHEN discount = 0
                THEN '0%'

            WHEN discount > 0 AND discount <= 0.10
                THEN '0-10%'

            WHEN discount > 0.10 AND discount <= 0.20
                THEN '10-20%'

            WHEN discount > 0.20 AND discount <= 0.30
                THEN '20-30%'

            WHEN discount > 0.30 AND discount <= 0.50
                THEN '30-50%'

            ELSE 'Above 50%'
        END AS discount_band,

        CASE
            WHEN discount = 0 THEN 1
            WHEN discount <= 0.10 THEN 2
            WHEN discount <= 0.20 THEN 3
            WHEN discount <= 0.30 THEN 4
            WHEN discount <= 0.50 THEN 5
            ELSE 6
        END AS band_order

    FROM sales

    WHERE discount IS NOT NULL
      AND discount >= 0
      AND discount <= 1
)

SELECT
    discount_band,

    COUNT(*) AS order_lines,

    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(SUM(sales), 2) AS total_sales,

    ROUND(SUM(profit), 2) AS total_profit,

    ROUND(
        100.0 * SUM(profit)
        / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct,

    ROUND(
        100.0 * AVG(discount),
        2
    ) AS avg_discount_pct,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN profit < 0 THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS loss_making_lines_pct

FROM discount_groups

GROUP BY
    discount_band,
    band_order

ORDER BY band_order;

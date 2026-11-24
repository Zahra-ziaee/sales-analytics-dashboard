
-- =====================================================
-- MONTHLY SALES GROWTH & ROLLING AVERAGE
-- CTE + LAG + WINDOW FUNCTIONS
-- =====================================================

WITH monthly_sales AS (
    SELECT
        order_year_month,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit
    FROM sales
    WHERE order_year_month IS NOT NULL
    GROUP BY order_year_month
),

sales_analysis AS (
    SELECT
        order_year_month,
        total_sales,
        total_profit,

        LAG(total_sales) OVER (
            ORDER BY order_year_month
        ) AS previous_month_sales,

        AVG(total_sales) OVER (
            ORDER BY order_year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_avg,

        COUNT(*) OVER (
            ORDER BY order_year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS months_in_window

    FROM monthly_sales
)

SELECT
    order_year_month,
    total_sales,
    total_profit,
    previous_month_sales,

    CASE
        WHEN previous_month_sales IS NULL
             OR previous_month_sales = 0
        THEN NULL
        ELSE ROUND(
            100.0 * (
                total_sales - previous_month_sales
            ) / previous_month_sales,
            2
        )
    END AS sales_mom_growth_pct,

    CASE
        WHEN months_in_window = 3
        THEN ROUND(rolling_avg, 2)
        ELSE NULL
    END AS sales_3month_rolling_avg

FROM sales_analysis
ORDER BY order_year_month;

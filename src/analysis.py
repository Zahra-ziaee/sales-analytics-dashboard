from pathlib import Path

import pandas as pd

from src.database import run_query


def calculate_main_kpis() -> pd.DataFrame:
    query = """
    SELECT
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
    FROM sales;
    """

    return run_query(query)


def sales_by_region() -> pd.DataFrame:
    query = """
    SELECT
        region,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
    FROM sales
    GROUP BY region
    ORDER BY total_sales DESC;
    """

    return run_query(query)


def sales_by_category() -> pd.DataFrame:
    query = """
    SELECT
        category,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin
    FROM sales
    GROUP BY category
    ORDER BY total_sales DESC;
    """

    return run_query(query)


def monthly_sales_trend() -> pd.DataFrame:
    query = """
    SELECT
        order_year_month,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit
    FROM sales
    GROUP BY order_year_month
    ORDER BY order_year_month;
    """

    return run_query(query)


def top_products_by_sales(limit: int = 10) -> pd.DataFrame:
    query = f"""
    SELECT
        product_name,
        category,
        sub_category,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit
    FROM sales
    GROUP BY product_name, category, sub_category
    ORDER BY total_sales DESC
    LIMIT {limit};
    """

    return run_query(query)


def save_analysis_outputs(output_dir: str = "results") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outputs = {
        "main_kpis.csv": calculate_main_kpis(),
        "sales_by_region.csv": sales_by_region(),
        "sales_by_category.csv": sales_by_category(),
        "monthly_sales_trend.csv": monthly_sales_trend(),
        "top_products_by_sales.csv": top_products_by_sales(),
    }

    for file_name, df in outputs.items():
        file_path = output_path / file_name
        df.to_csv(file_path, index=False)
        print(f"Saved analysis output: {file_path}")
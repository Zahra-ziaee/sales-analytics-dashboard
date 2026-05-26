from src.data_loader import load_raw_sales_data, print_data_summary
from src.cleaning import clean_sales_data, save_cleaned_data
from src.database import create_database
from src.analysis import (
    calculate_main_kpis,
    sales_by_region,
    sales_by_category,
    monthly_sales_trend,
    top_products_by_sales,
    save_analysis_outputs,
)
from src.visualization import (
    plot_sales_by_region,
    plot_sales_by_category,
    plot_monthly_sales_trend,
)


def main():
    print("=" * 60)
    print("Sales Analytics Dashboard Project")
    print("=" * 60)

    raw_df = load_raw_sales_data()

    print("\nRaw Data Summary:")
    print_data_summary(raw_df)

    cleaned_df = clean_sales_data(raw_df)

    print("\nCleaned data shape:")
    print(cleaned_df.shape)

    print("\nCleaned columns:")
    for column in cleaned_df.columns:
        print(f"- {column}")

    save_cleaned_data(cleaned_df)
    create_database(cleaned_df)

    print("\nMain KPIs:")
    main_kpis = calculate_main_kpis()
    print(main_kpis)

    print("\nSales by Region:")
    region_df = sales_by_region()
    print(region_df)

    print("\nSales by Category:")
    category_df = sales_by_category()
    print(category_df)

    print("\nMonthly Sales Trend:")
    monthly_df = monthly_sales_trend()
    print(monthly_df.head())

    print("\nTop Products by Sales:")
    top_products_df = top_products_by_sales()
    print(top_products_df)

    save_analysis_outputs()

    plot_sales_by_region(region_df)
    plot_sales_by_category(category_df)
    plot_monthly_sales_trend(monthly_df)


if __name__ == "__main__":
    main()
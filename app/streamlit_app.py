from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"


@st.cache_data
def load_csv_outputs():
    main_kpis = pd.read_csv(RESULTS_DIR / "main_kpis.csv")
    sales_by_region = pd.read_csv(RESULTS_DIR / "sales_by_region.csv")
    sales_by_category = pd.read_csv(RESULTS_DIR / "sales_by_category.csv")
    monthly_sales_trend = pd.read_csv(RESULTS_DIR / "monthly_sales_trend.csv")
    top_products = pd.read_csv(RESULTS_DIR / "top_products_by_sales.csv")

    return (
        main_kpis,
        sales_by_region,
        sales_by_category,
        monthly_sales_trend,
        top_products,
    )


def format_currency(value):
    return f"${value:,.2f}"


def plot_monthly_sales_trend(monthly_sales_trend: pd.DataFrame):
    monthly_df = monthly_sales_trend[["order_year_month", "total_sales"]].copy()
    monthly_df["order_year_month"] = monthly_df["order_year_month"].astype(str)
    monthly_df = monthly_df.sort_values("order_year_month").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        monthly_df.index,
        monthly_df["total_sales"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")

    tick_positions = list(range(0, len(monthly_df), 4))
    tick_labels = monthly_df.loc[tick_positions, "order_year_month"]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")

    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig


def plot_profit_margin_by_category(sales_by_category: pd.DataFrame):
    margin_df = sales_by_category[["category", "profit_margin"]].copy()
    margin_df["profit_margin_percent"] = margin_df["profit_margin"] * 100
    margin_df = margin_df.sort_values("profit_margin_percent", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.barh(
        margin_df["category"],
        margin_df["profit_margin_percent"],
    )

    ax.set_title("Profit Margin by Category")
    ax.set_xlabel("Profit Margin (%)")
    ax.set_ylabel("Category")

    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()

    return fig


def main():
    st.set_page_config(
        page_title="Sales Analytics Dashboard",
        layout="wide",
    )

    st.title("📊 Superstore Sales Analytics Dashboard")

    st.write(
        "This dashboard analyzes sales, profit, regional performance, "
        "category profitability, monthly trends, and top products."
    )

    try:
        (
            main_kpis,
            sales_by_region,
            sales_by_category,
            monthly_sales_trend,
            top_products,
        ) = load_csv_outputs()

    except FileNotFoundError as error:
        st.error("Required result files were not found.")
        st.write("Please run the main pipeline first:")
        st.code("python main.py")
        st.write(error)
        return

    kpis = main_kpis.iloc[0]

    total_sales = float(kpis["total_sales"])
    total_profit = float(kpis["total_profit"])
    total_orders = int(kpis["total_orders"])
    total_customers = int(kpis["total_customers"])
    profit_margin = float(kpis["profit_margin"])

    st.subheader("Main KPIs")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Sales", format_currency(total_sales))
    col2.metric("Total Profit", format_currency(total_profit))
    col3.metric("Profit Margin", f"{profit_margin * 100:.2f}%")
    col4.metric("Total Orders", f"{total_orders:,}")
    col5.metric("Total Customers", f"{total_customers:,}")

    st.divider()

    st.subheader("Sales Performance Overview")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Sales by Region")
        region_df = sales_by_region[["region", "total_sales"]].copy()
        region_df = region_df.sort_values("total_sales", ascending=False)
        region_df = region_df.set_index("region")
        st.bar_chart(region_df)

    with col_right:
        st.markdown("### Sales by Category")
        category_df = sales_by_category[["category", "total_sales"]].copy()
        category_df = category_df.sort_values("total_sales", ascending=False)
        category_df = category_df.set_index("category")
        st.bar_chart(category_df)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.pyplot(plot_profit_margin_by_category(sales_by_category))

    with col_right:
        st.pyplot(plot_monthly_sales_trend(monthly_sales_trend))

    st.divider()

    st.subheader("Top Products by Sales")

    top_products_display = top_products.copy()

    top_products_display["total_sales"] = top_products_display["total_sales"].apply(
        format_currency
    )
    top_products_display["total_profit"] = top_products_display["total_profit"].apply(
        format_currency
    )

    st.dataframe(
        top_products_display,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Business Insights")

    st.markdown(
        """
        - **West** is the strongest region by total sales and total profit.
        - **Technology** is the strongest category in both sales and profit.
        - **Furniture** has high sales but weak profit margin, which may indicate pricing, discount, or cost issues.
        - Some high-sales products generate negative profit, so product performance should be evaluated using both revenue and profitability.
        - Monthly sales trends help identify seasonality and changes in sales performance over time.
        """
    )


if __name__ == "__main__":
    main()
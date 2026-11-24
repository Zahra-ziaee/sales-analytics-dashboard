
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# =====================================================
# PROJECT CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"


# =====================================================
# DATA LOADING
# =====================================================

@st.cache_data
def load_csv_outputs():
    """Load the original dashboard reports."""

    filenames = [
        "main_kpis.csv",
        "sales_by_region.csv",
        "sales_by_category.csv",
        "monthly_sales_trend.csv",
        "top_products_by_sales.csv",
    ]

    return tuple(
        pd.read_csv(RESULTS_DIR / name)
        for name in filenames
    )


def load_optional_report(filename):
    """Load an additional report if available."""

    file_path = RESULTS_DIR / filename

    if not file_path.exists():
        return None

    return pd.read_csv(file_path)


# =====================================================
# HELPERS
# =====================================================

def format_currency(value):

    value = float(value)

    if value < 0:
        return f"-${abs(value):,.2f}"

    return f"${value:,.2f}"


def show_figure(fig):

    st.pyplot(fig)
    plt.close(fig)


# =====================================================
# ORIGINAL MONTHLY SALES CHART
# =====================================================

def plot_monthly_sales_trend(monthly_sales_trend):

    df = (
        monthly_sales_trend
        .sort_values("order_year_month")
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df.index,
        df["total_sales"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales ($)")

    ticks = list(range(0, len(df), 4))

    ax.set_xticks(ticks)

    ax.set_xticklabels(
        df.loc[ticks, "order_year_month"],
        rotation=45,
        ha="right",
    )

    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig


# =====================================================
# CATEGORY PROFITABILITY
# =====================================================

def plot_profit_margin_by_category(sales_by_category):

    df = sales_by_category[
        ["category", "profit_margin"]
    ].copy()

    df["margin_pct"] = df["profit_margin"] * 100

    df = df.sort_values("margin_pct")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.barh(
        df["category"],
        df["margin_pct"],
    )

    ax.set_title("Profit Margin by Category")
    ax.set_xlabel("Profit Margin (%)")
    ax.set_ylabel("Category")

    ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()

    return fig


# =====================================================
# ADVANCED MONTHLY SALES CHART
# =====================================================

def plot_advanced_monthly_sales(monthly_df):

    df = (
        monthly_df
        .sort_values("order_year_month")
        .reset_index(drop=True)
    )

    x = range(len(df))

    fig, ax = plt.subplots(figsize=(12, 5.5))

    ax.plot(
        x,
        df["total_sales"],
        color="#2878B5",
        marker="o",
        markersize=4,
        linewidth=1.8,
        alpha=0.8,
        label="Actual Monthly Sales",
    )

    ax.plot(
        x,
        df["sales_3month_rolling_avg"],
        color="#E76F51",
        linewidth=2.8,
        label="3-Month Rolling Average",
    )

    ticks = list(range(0, len(df), 4))

    if len(df) - 1 not in ticks:
        ticks.append(len(df) - 1)

    ax.set_xticks(ticks)

    ax.set_xticklabels(
        df.loc[ticks, "order_year_month"],
        rotation=45,
        ha="right",
    )

    ax.set_title(
        "Monthly Sales vs. 3-Month Rolling Average"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Sales ($)")

    ax.grid(
        alpha=0.2,
        linestyle="--",
    )

    ax.legend(loc="upper left")

    fig.tight_layout()

    return fig


# =====================================================
# ADVANCED MONTHLY SALES ANALYSIS
# =====================================================

def show_advanced_monthly_analysis():

    st.divider()

    st.subheader(
        "Advanced Monthly Sales Analysis"
    )

    st.write(
        "Monthly sales growth calculated using SQL "
        "LAG(), alongside a three-month rolling average."
    )

    df = load_optional_report(
        "advanced_monthly_sales.csv"
    )

    if df is None:
        st.warning(
            "Missing results/advanced_monthly_sales.csv. "
            "Generate the report from the SQL analysis."
        )
        return

    required_columns = {
        "order_year_month",
        "total_sales",
        "total_profit",
        "previous_month_sales",
        "sales_mom_growth_pct",
        "sales_3month_rolling_avg",
    }

    missing = required_columns - set(df.columns)

    if df.empty or missing:
        st.error(
            "Monthly report is empty or missing columns: "
            f"{sorted(missing)}"
        )
        return

    df = (
        df.sort_values("order_year_month")
        .reset_index(drop=True)
    )

    # -------------------------------------------------
    # LATEST MONTH KPIS
    # -------------------------------------------------

    latest = df.iloc[-1]

    latest_month = str(
        latest["order_year_month"]
    )

    latest_sales = float(
        latest["total_sales"]
    )

    latest_growth = latest[
        "sales_mom_growth_pct"
    ]

    latest_rolling = latest[
        "sales_3month_rolling_avg"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        f"Sales in {latest_month}",
        format_currency(latest_sales),
    )

    col2.metric(
        "Latest MoM Growth",
        (
            f"{float(latest_growth):+.2f}%"
            if pd.notna(latest_growth)
            else "N/A"
        ),
    )

    col3.metric(
        "Latest 3-Month Average",
        (
            format_currency(latest_rolling)
            if pd.notna(latest_rolling)
            else "N/A"
        ),
    )

    # -------------------------------------------------
    # ADVANCED MONTHLY CHART
    # -------------------------------------------------

    fig = plot_advanced_monthly_sales(df)

    show_figure(fig)

    st.caption(
        "Each three-month average uses the current "
        "month and two previous months. "
        "The first two months do not have a complete "
        "three-month window."
    )

    # -------------------------------------------------
    # HIGHEST AND LOWEST MONTHLY GROWTH
    # -------------------------------------------------

    valid_growth = df.dropna(
        subset=["sales_mom_growth_pct"]
    )

    if not valid_growth.empty:

        highest_growth = valid_growth.loc[
            valid_growth[
                "sales_mom_growth_pct"
            ].idxmax()
        ]

        lowest_growth = valid_growth.loc[
            valid_growth[
                "sales_mom_growth_pct"
            ].idxmin()
        ]

        left_col, right_col = st.columns(2)

        # Corrected f-string
        left_col.metric(
            "Highest Observed MoM Growth",
            f"{float(highest_growth['sales_mom_growth_pct']):+.2f}%",
        )

        left_col.caption(
            f"Month: {highest_growth['order_year_month']}"
        )

        # Corrected f-string
        right_col.metric(
            "Lowest Observed MoM Growth",
            f"{float(lowest_growth['sales_mom_growth_pct']):+.2f}%",
        )

        right_col.caption(
            f"Month: {lowest_growth['order_year_month']}"
        )

    # -------------------------------------------------
    # BUSINESS INTERPRETATION
    # -------------------------------------------------

    st.info(
        "Monthly sales vary considerably. "
        "A rolling average can help reveal a "
        "smoother historical trend without removing "
        "the original observations."
    )

    st.caption(
        "Large MoM percentages may arise from small "
        "previous-month sales. These descriptive "
        "changes do not establish causes or seasonality."
    )

    # -------------------------------------------------
    # DETAILED DATA
    # -------------------------------------------------

    with st.expander(
        "View Monthly Growth & Rolling Average Data"
    ):

        display_df = df.rename(
            columns={
                "order_year_month": "Month",
                "total_sales": "Sales ($)",
                "total_profit": "Profit ($)",
                "previous_month_sales": (
                    "Previous Month Sales ($)"
                ),
                "sales_mom_growth_pct": (
                    "MoM Growth (%)"
                ),
                "sales_3month_rolling_avg": (
                    "Rolling Average 3M ($)"
                ),
            }
        )

        display_df = display_df.sort_values(
            "Month",
            ascending=False,
        )

        st.dataframe(
            display_df.round(2),
            use_container_width=True,
            hide_index=True,
        )


# =====================================================
# DISCOUNT PROFIT MARGIN CHART
# =====================================================

def plot_discount_profit_margin(discount_df):

    fig, ax = plt.subplots(figsize=(9, 5))

    colors = [
        "#2E7D32" if value >= 0 else "#C62828"
        for value in discount_df["profit_margin_pct"]
    ]

    ax.bar(
        discount_df["discount_band"],
        discount_df["profit_margin_pct"],
        color=colors,
    )

    ax.axhline(
        0,
        color="#333333",
        linewidth=1,
    )

    ax.set_title(
        "Profit Margin by Discount Band"
    )

    ax.set_xlabel("Discount Band")
    ax.set_ylabel("Profit Margin (%)")

    ax.tick_params(
        axis="x",
        labelrotation=25,
    )

    ax.grid(
        axis="y",
        alpha=0.2,
        linestyle="--",
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    return fig


# =====================================================
# DISCOUNT LOSS RATE CHART
# =====================================================

def plot_discount_loss_rate(discount_df):

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.bar(
        discount_df["discount_band"],
        discount_df["loss_making_lines_pct"],
        color="#D97706",
    )

    ax.set_title(
        "Loss-Making Order Lines by Discount Band"
    )

    ax.set_xlabel("Discount Band")

    ax.set_ylabel(
        "Loss-Making Order Lines (%)"
    )

    ax.set_ylim(0, 105)

    ax.tick_params(
        axis="x",
        labelrotation=25,
    )

    ax.grid(
        axis="y",
        alpha=0.2,
        linestyle="--",
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    return fig


# =====================================================
# DISCOUNT & PROFITABILITY ANALYSIS
# =====================================================

def show_discount_analysis():

    st.divider()

    st.subheader(
        "Discount & Profitability Analysis"
    )

    st.write(
        "Explore the observed relationship between "
        "discount levels, profit margins, and "
        "loss-making order lines."
    )

    df = load_optional_report(
        "discount_band_analysis.csv"
    )

    if df is None:
        st.warning(
            "Missing results/discount_band_analysis.csv."
        )
        return

    required_columns = {
        "discount_band",
        "order_lines",
        "total_orders",
        "total_sales",
        "total_profit",
        "profit_margin_pct",
        "avg_discount_pct",
        "loss_making_lines_pct",
    }

    missing = required_columns - set(df.columns)

    if df.empty or missing:
        st.error(
            "Discount report is empty or missing columns: "
            f"{sorted(missing)}"
        )
        return

    # -------------------------------------------------
    # SORT DISCOUNT BANDS
    # -------------------------------------------------

    discount_order = [
        "0%",
        "0-10%",
        "10-20%",
        "20-30%",
        "30-50%",
        "Above 50%",
    ]

    df = df.copy()

    df["band_order"] = df["discount_band"].map(
        {
            band: index
            for index, band in enumerate(discount_order)
        }
    )

    df = (
        df.sort_values("band_order")
        .reset_index(drop=True)
    )

    # -------------------------------------------------
    # DISCOUNT KPIS
    # -------------------------------------------------

    no_discount = df[
        df["discount_band"] == "0%"
    ]

    high_discount = df[
        df["discount_band"] == "Above 50%"
    ]

    col1, col2, col3 = st.columns(3)

    if not no_discount.empty:
        col1.metric(
            "Margin Without Discount",
            f"{no_discount.iloc[0]['profit_margin_pct']:.2f}%",
        )

    if not high_discount.empty:
        col2.metric(
            "Margin Above 50% Discount",
            f"{high_discount.iloc[0]['profit_margin_pct']:.2f}%",
        )

        col3.metric(
            "Loss-Making Lines Above 50%",
            f"{high_discount.iloc[0]['loss_making_lines_pct']:.2f}%",
        )

    # -------------------------------------------------
    # DISCOUNT CHARTS
    # -------------------------------------------------

    left_col, right_col = st.columns(2)

    with left_col:
        show_figure(
            plot_discount_profit_margin(df)
        )

    with right_col:
        show_figure(
            plot_discount_loss_rate(df)
        )

    # -------------------------------------------------
    # INSIGHTS
    # -------------------------------------------------

    st.info(
        "In this dataset, higher discount bands "
        "are associated with lower observed profit "
        "margins. All order lines in the above-50% "
        "discount band were loss-making."
    )

    st.caption(
        "Observational associations are not causal "
        "effects. Product mix and costs may explain "
        "some differences. Distinct order counts "
        "cannot be summed across discount bands "
        "because one order may contain several lines."
    )

    with st.expander(
        "View Detailed Discount Analysis"
    ):

        st.dataframe(
            df.drop(columns=["band_order"]).round(2),
            use_container_width=True,
            hide_index=True,
        )


# =====================================================
# LOSS-MAKING PRODUCTS CHART
# =====================================================

def plot_loss_making_products(products_df):

    losses = products_df[
        products_df["total_profit"] < 0
    ]

    losses = (
        losses
        .sort_values("total_profit")
        .head(10)
    )

    if losses.empty:
        return None

    labels = [
        name[:43] + "..."
        if len(name) > 43
        else name
        for name in losses["product_name"]
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        labels,
        losses["total_profit"],
        color="#C62828",
    )

    ax.set_title(
        "Products with the Largest Monetary Losses"
    )

    ax.set_xlabel("Total Profit / Loss ($)")
    ax.set_ylabel("Product")

    ax.axvline(
        0,
        color="#333333",
        linewidth=1,
    )

    ax.grid(
        axis="x",
        alpha=0.2,
        linestyle="--",
    )

    ax.set_axisbelow(True)

    # Largest loss at the top
    ax.invert_yaxis()

    fig.tight_layout()

    return fig


# =====================================================
# HIGH-SALES, LOW-PROFIT PRODUCTS
# =====================================================

def show_high_sales_low_profit():

    st.divider()

    st.subheader(
        "High-Sales, Low-Profit Products"
    )

    st.write(
        "Products in the highest sales quartile "
        "with margins below the company-wide "
        "profit margin."
    )

    df = load_optional_report(
        "high_sales_low_profit.csv"
    )

    if df is None:
        st.warning(
            "Missing results/high_sales_low_profit.csv."
        )
        return

    if df.empty:
        st.info(
            "No products were returned by the priority query."
        )
        return

    required_columns = {
        "product_id",
        "product_name",
        "category",
        "total_sales",
        "total_profit",
        "profit_margin_pct",
        "company_profit_margin_pct",
        "sales_rank",
        "sales_quartile",
        "business_flag",
    }

    missing = required_columns - set(df.columns)

    if missing:
        st.error(
            f"Product report missing columns: {sorted(missing)}"
        )
        return

    # -------------------------------------------------
    # SORT BY MONETARY LOSS
    # -------------------------------------------------

    df = (
        df.sort_values("total_profit")
        .reset_index(drop=True)
    )

    losses = df[
        df["total_profit"] < 0
    ]

    # -------------------------------------------------
    # PRODUCT KPIS
    # -------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Products in Priority Report",
        f"{len(df):,}",
    )

    col2.metric(
        "Loss-Making Products in Report",
        f"{len(losses):,}",
    )

    col3.metric(
        "Company Profit Margin",
        f"{df.iloc[0]['company_profit_margin_pct']:.2f}%",
    )

    # -------------------------------------------------
    # PRODUCT CHART
    # -------------------------------------------------

    fig = plot_loss_making_products(df)

    if fig is not None:
        show_figure(fig)

    # -------------------------------------------------
    # PRIORITY FINDING
    # -------------------------------------------------

    if not losses.empty:

        worst = losses.iloc[0]

        st.warning(
            f"Priority Finding: {worst['product_name']} "
            "has the largest monetary loss among "
            "products in this report: "
            f"{format_currency(worst['total_profit'])}. "
            "Its observed margin is "
            f"{worst['profit_margin_pct']:.2f}%."
        )

    st.caption(
        "The CSV contains up to 20 products returned "
        "by the SQL query, not the full catalog. "
        "NTILE(4) divides products into approximately "
        "equal-sized sales groups. "
        "This analysis does not establish causation."
    )

    # -------------------------------------------------
    # PRODUCT DETAILS
    # -------------------------------------------------

    st.markdown(
        "#### Product Profitability Details"
    )

    display_columns = [
        "product_name",
        "category",
        "total_sales",
        "total_profit",
        "profit_margin_pct",
        "company_profit_margin_pct",
        "sales_rank",
        "business_flag",
    ]

    display_df = df[display_columns].rename(
        columns={
            "product_name": "Product",
            "category": "Category",
            "total_sales": "Sales ($)",
            "total_profit": "Profit ($)",
            "profit_margin_pct": "Margin (%)",
            "company_profit_margin_pct": (
                "Company Margin (%)"
            ),
            "sales_rank": "Sales Rank",
            "business_flag": "Business Flag",
        }
    )

    st.dataframe(
        display_df.round(2),
        use_container_width=True,
        hide_index=True,
    )


# =====================================================
# MAIN DASHBOARD
# =====================================================

def main():

    st.set_page_config(
        page_title="Sales Analytics Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title(
        "📊 Superstore Sales Analytics Dashboard"
    )

    st.write(
        "Explore sales performance, profitability, "
        "regional trends, product rankings, "
        "advanced monthly analysis, and business insights."
    )

    # -------------------------------------------------
    # LOAD ORIGINAL RESULTS
    # -------------------------------------------------

    try:
        (
            main_kpis,
            sales_by_region,
            sales_by_category,
            monthly_sales_trend,
            top_products,
        ) = load_csv_outputs()

    except (FileNotFoundError, pd.errors.EmptyDataError) as error:

        st.error(
            "Required report files are missing or empty. "
            "Run python main.py first."
        )

        st.write(error)
        return

    # -------------------------------------------------
    # MAIN KPIS
    # -------------------------------------------------

    kpis = main_kpis.iloc[0]

    total_sales = float(kpis["total_sales"])
    total_profit = float(kpis["total_profit"])
    total_orders = int(kpis["total_orders"])
    total_customers = int(kpis["total_customers"])
    profit_margin = float(kpis["profit_margin"])

    st.subheader("Main KPIs")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total Sales",
            f"${total_sales / 1_000_000:.2f}M",
        )

        st.caption(
            f"Exact: {format_currency(total_sales)}"
        )

    col2.metric(
        "Total Profit",
        format_currency(total_profit),
    )

    col3.metric(
        "Profit Margin",
        f"{profit_margin * 100:.2f}%",
    )

    col4.metric(
        "Total Orders",
        f"{total_orders:,}",
    )

    col5.metric(
        "Total Customers",
        f"{total_customers:,}",
    )

    # -------------------------------------------------
    # SALES PERFORMANCE OVERVIEW
    # -------------------------------------------------

    st.divider()

    st.subheader(
        "Sales Performance Overview"
    )

    left_col, right_col = st.columns(2)

    with left_col:

        st.markdown("### Sales by Region")

        region_df = sales_by_region[
            ["region", "total_sales"]
        ].copy()

        region_df = region_df.sort_values(
            "total_sales",
            ascending=False,
        )

        st.bar_chart(
            region_df.set_index("region")
        )

    with right_col:

        st.markdown("### Sales by Category")

        category_df = sales_by_category[
            ["category", "total_sales"]
        ].copy()

        category_df = category_df.sort_values(
            "total_sales",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index("category")
        )

    # -------------------------------------------------
    # ORIGINAL CHARTS
    # -------------------------------------------------

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:
        show_figure(
            plot_profit_margin_by_category(
                sales_by_category
            )
        )

    with right_col:
        show_figure(
            plot_monthly_sales_trend(
                monthly_sales_trend
            )
        )

    # -------------------------------------------------
    # ADVANCED MONTHLY ANALYSIS
    # -------------------------------------------------

    show_advanced_monthly_analysis()

    # -------------------------------------------------
    # TOP PRODUCTS BY SALES
    # -------------------------------------------------

    st.divider()

    st.subheader(
        "Top Products by Sales"
    )

    top_products_display = top_products.copy()

    top_products_display["total_sales"] = (
        top_products_display["total_sales"]
        .apply(format_currency)
    )

    top_products_display["total_profit"] = (
        top_products_display["total_profit"]
        .apply(format_currency)
    )

    st.dataframe(
        top_products_display,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------
    # BUSINESS ANALYSIS
    # -------------------------------------------------

    show_discount_analysis()

    show_high_sales_low_profit()

    # -------------------------------------------------
    # BUSINESS INSIGHTS
    # -------------------------------------------------

    st.divider()

    st.subheader("Business Insights")

    st.markdown(
        """
        - **Sales trends:** Rolling averages provide a
          smoother view of monthly sales fluctuations.

        - **Regional performance:** Sales and profit
          vary across geographic regions.

        - **Category profitability:** High sales do
          not necessarily imply high profit margins.

        - **Product-level risk:** Some higher-selling
          products generate monetary losses.

        - **Discount analysis:** Larger discount bands
          are associated with weaker observed margins
          in this historical dataset.

        - **Decision support:** These findings identify
          candidates for further pricing, discount,
          and cost investigations.
        """
    )

    st.caption(
        "Historical observational analysis only. "
        "These findings do not establish that a "
        "particular pricing or discount change "
        "would cause higher profit."
    )


if __name__ == "__main__":
    main()

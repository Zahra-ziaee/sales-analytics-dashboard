import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURES_DIR


def plot_sales_by_region(region_df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.bar(region_df["region"], region_df["total_sales"])
    plt.title("Total Sales by Region")
    plt.xlabel("Region")
    plt.ylabel("Total Sales")
    plt.tight_layout()

    output_path = FIGURES_DIR / "sales_by_region.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved chart: {output_path}")


def plot_sales_by_category(category_df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.bar(category_df["category"], category_df["total_sales"])
    plt.title("Total Sales by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Sales")
    plt.tight_layout()

    output_path = FIGURES_DIR / "sales_by_category.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved chart: {output_path}")


def plot_monthly_sales_trend(monthly_df: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    monthly_df = monthly_df.copy()
    monthly_df = monthly_df.dropna(subset=["order_year_month"])
    monthly_df["order_year_month"] = monthly_df["order_year_month"].astype(str)

    plt.figure(figsize=(14, 6))
    plt.plot(
        monthly_df["order_year_month"],
        monthly_df["total_sales"],
        marker="o",
    )
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Sales")
    plt.xticks(rotation=90)
    plt.tight_layout()

    output_path = FIGURES_DIR / "monthly_sales_trend.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved chart: {output_path}")
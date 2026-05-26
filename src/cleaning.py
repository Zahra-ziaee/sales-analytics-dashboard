import pandas as pd

from src.config import PROCESSED_SUPERSTORE_FILE


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = (
        df.columns
        .str.replace("ï»¿", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = clean_column_names(df)

    date_columns = ["order_date", "ship_date"]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                dayfirst=True,
            )

    numeric_columns = [
        "sales",
        "quantity",
        "discount",
        "profit",
        "postal_code",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.drop_duplicates()

    # Remove rows with invalid order dates, because they cannot be used in time-series analysis.
    df = df.dropna(subset=["order_date"])

    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)

    df["profit_margin"] = df.apply(
        lambda row: row["profit"] / row["sales"] if row["sales"] != 0 else 0,
        axis=1,
    )

    return df


def save_cleaned_data(df: pd.DataFrame) -> None:
    PROCESSED_SUPERSTORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_SUPERSTORE_FILE, index=False)

    print(f"\nCleaned data saved to: {PROCESSED_SUPERSTORE_FILE}")
import pandas as pd

from src.config import RAW_SUPERSTORE_FILE


def load_raw_sales_data() -> pd.DataFrame:
    if not RAW_SUPERSTORE_FILE.exists():
        raise FileNotFoundError(f"File not found: {RAW_SUPERSTORE_FILE}")

    df = pd.read_csv(RAW_SUPERSTORE_FILE, encoding="utf-8-sig")

    df.columns = (
        df.columns
        .str.replace("ï»¿", "", regex=False)
        .str.strip()
    )

    return df


def print_data_summary(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("Superstore Sales Dataset Summary")
    print("=" * 60)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nFirst rows:")
    print(df.head())
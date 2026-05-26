from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

RAW_SUPERSTORE_FILE = RAW_DATA_DIR / "superstore.csv"
PROCESSED_SUPERSTORE_FILE = PROCESSED_DATA_DIR / "superstore_cleaned.csv"

DATABASE_FILE = PROJECT_ROOT / "sales_analytics.db"
SALES_TABLE_NAME = "sales"

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "sales_analytics.db"
SQL_DIR = ROOT / "sql"
RESULTS_DIR = ROOT / "results"


REPORTS = {
    "advanced_sales_analysis.sql": "advanced_monthly_sales.csv",
    "discount_band_analysis.sql": "discount_band_analysis.csv",
    "high_sales_low_profit.sql": "high_sales_low_profit.csv",
}


def main():
    if not DATABASE.is_file():
        raise FileNotFoundError(
            "SQLite database not found. "
            "Run 'python main.py' first."
        )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE) as conn:

        table_exists = conn.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'sales'
            """
        ).fetchone()[0]

        if not table_exists:
            raise RuntimeError(
                "The SQLite database does not contain "
                "the required 'sales' table."
            )

        for sql_filename, csv_filename in REPORTS.items():

            sql_path = SQL_DIR / sql_filename
            output_path = RESULTS_DIR / csv_filename

            if not sql_path.is_file():
                raise FileNotFoundError(
                    f"SQL file not found: {sql_path}"
                )

            query = sql_path.read_text(
                encoding="utf-8-sig"
            )

            result = pd.read_sql_query(
                query,
                conn,
            )

            result.to_csv(
                output_path,
                index=False,
            )

            print(
                f"PASS: {csv_filename} "
                f"({result.shape[0]} rows, "
                f"{result.shape[1]} columns)"
            )

    print("\nAll advanced reports exported successfully.")


if __name__ == "__main__":
    main()

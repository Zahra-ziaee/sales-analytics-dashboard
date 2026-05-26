import sqlite3
import pandas as pd

from src.config import DATABASE_FILE, SALES_TABLE_NAME


def create_database(df: pd.DataFrame) -> None:
    connection = sqlite3.connect(DATABASE_FILE)

    df.to_sql(
        SALES_TABLE_NAME,
        connection,
        if_exists="replace",
        index=False,
    )

    connection.close()

    print(f"\nSQLite database created: {DATABASE_FILE}")
    print(f"Table created: {SALES_TABLE_NAME}")


def run_query(query: str) -> pd.DataFrame:
    connection = sqlite3.connect(DATABASE_FILE)
    result_df = pd.read_sql_query(query, connection)
    connection.close()

    return result_df
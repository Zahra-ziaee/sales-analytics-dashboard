
import sqlite3
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "sales_analytics.db"
REPORT = ROOT / "results" / "high_sales_low_profit.csv"


class TestProductRanking(unittest.TestCase):

    def test_product_priority_ranking(self):

        with sqlite3.connect(DATABASE) as conn:

            products = pd.read_sql_query(
                """
                SELECT
                    product_id,
                    product_name,
                    category,
                    sub_category,
                    SUM(sales) AS total_sales,
                    SUM(profit) AS total_profit
                FROM sales
                WHERE product_id IS NOT NULL
                GROUP BY
                    product_id,
                    product_name,
                    category,
                    sub_category
                """,
                conn,
            )

            company_margin = conn.execute(
                """
                SELECT
                    100.0 * SUM(profit)
                    / NULLIF(SUM(sales), 0)
                FROM sales
                """
            ).fetchone()[0]

        # Reproduce sales ordering independently.
        products = products.sort_values(
            ["total_sales", "product_id", "product_name"],
            ascending=[False, True, True],
        ).reset_index(drop=True)

        # Reproduce SQLite NTILE(4).
        n = len(products)
        base, remainder = divmod(n, 4)

        sizes = [
            base + (1 if i < remainder else 0)
            for i in range(4)
        ]

        products["sales_quartile"] = np.repeat(
            [1, 2, 3, 4],
            sizes,
        )

        # Reproduce DENSE_RANK().
        products["sales_rank"] = (
            products["total_sales"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )

        products["margin_pct"] = (
            100.0
            * products["total_profit"]
            / products["total_sales"].replace(0, np.nan)
        )

        # Select the highest sales quartile,
        # then products below company margin.
        eligible = products.loc[
            (products["sales_quartile"] == 1)
            & (products["margin_pct"] < company_margin)
        ]

        expected = (
            eligible
            .sort_values(
                ["total_profit", "total_sales"],
                ascending=[True, False],
            )
            .head(20)
        )

        actual = pd.read_csv(REPORT)

        keys = [
            "product_id",
            "product_name",
            "category",
            "sub_category",
        ]

        # Compare the exact selected product records.
        expected_keys = list(
            expected[keys].itertuples(index=False, name=None)
        )

        actual_keys = list(
            actual[keys].itertuples(index=False, name=None)
        )

        self.assertEqual(
            actual_keys,
            expected_keys,
        )

        # Verify stored rankings.
        for column in ["sales_rank", "sales_quartile"]:
            self.assertEqual(
                actual[column].tolist(),
                expected[column].tolist(),
            )

        print(
            f"\nPASS: Verified {len(actual)} "
            f"priority products against {n} "
            "product records."
        )


if __name__ == "__main__":
    unittest.main()


import sqlite3
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "sales_analytics.db"
RESULTS = ROOT / "results"


class TestBusinessMetrics(unittest.TestCase):

    def test_monthly_sales_calculations(self):
        """Validate monthly growth and rolling averages."""

        with sqlite3.connect(DATABASE) as conn:
            raw = pd.read_sql_query(
                """
                SELECT order_year_month, sales, profit
                FROM sales
                WHERE order_year_month IS NOT NULL
                """,
                conn,
            )

        expected = (
            raw.groupby("order_year_month", as_index=False)
            .agg(
                total_sales=("sales", "sum"),
                total_profit=("profit", "sum"),
            )
            .sort_values("order_year_month")
            .reset_index(drop=True)
        )

        expected["total_sales"] = (
            expected["total_sales"].round(2)
        )

        expected["total_profit"] = (
            expected["total_profit"].round(2)
        )

        expected["growth"] = (
            expected["total_sales"]
            .pct_change(fill_method=None) * 100
        )

        expected["rolling"] = (
            expected["total_sales"]
            .rolling(3, min_periods=3)
            .mean()
        )

        actual = (
            pd.read_csv(
                RESULTS / "advanced_monthly_sales.csv"
            )
            .sort_values("order_year_month")
            .reset_index(drop=True)
        )

        self.assertEqual(len(actual), 48)

        self.assertEqual(
            actual["order_year_month"].tolist(),
            expected["order_year_month"].tolist(),
        )

        comparisons = {
            "total_sales": "total_sales",
            "total_profit": "total_profit",
            "sales_mom_growth_pct": "growth",
            "sales_3month_rolling_avg": "rolling",
        }

        for actual_col, expected_col in comparisons.items():
            with self.subTest(column=actual_col):
                self.assertTrue(
                    np.allclose(
                        actual[actual_col],
                        expected[expected_col],
                        atol=0.011,
                        equal_nan=True,
                    ),
                    f"Mismatch in {actual_col}",
                )

    def test_discount_band_calculations(self):
        """Validate discount bands against source rows."""

        with sqlite3.connect(DATABASE) as conn:
            raw = pd.read_sql_query(
                """
                SELECT order_id, sales, profit, discount
                FROM sales
                WHERE discount BETWEEN 0 AND 1
                """,
                conn,
            )

        labels = [
            "0%",
            "0-10%",
            "10-20%",
            "20-30%",
            "30-50%",
            "Above 50%",
        ]

        raw["discount_band"] = pd.cut(
            raw["discount"],
            bins=[-0.000001, 0, 0.1, 0.2, 0.3, 0.5, 1],
            labels=labels,
            include_lowest=True,
        )

        raw["is_loss"] = (
            raw["profit"] < 0
        ).astype(int)

        expected = (
            raw.groupby(
                "discount_band",
                observed=True,
            )
            .agg(
                order_lines=("order_id", "size"),
                total_orders=("order_id", "nunique"),
                total_sales=("sales", "sum"),
                total_profit=("profit", "sum"),
                avg_discount_pct=("discount", "mean"),
                loss_making_lines_pct=("is_loss", "mean"),
            )
            .reset_index()
        )

        expected["avg_discount_pct"] *= 100
        expected["loss_making_lines_pct"] *= 100

        expected["profit_margin_pct"] = (
            100 * expected["total_profit"]
            / expected["total_sales"]
        )

        actual = pd.read_csv(
            RESULTS / "discount_band_analysis.csv"
        )

        self.assertEqual(len(actual), 6)

        merged = actual.merge(
            expected,
            on="discount_band",
            suffixes=("_actual", "_expected"),
            validate="one_to_one",
        )

        self.assertEqual(len(merged), 6)

        for column in ["order_lines", "total_orders"]:
            self.assertTrue(
                (
                    merged[f"{column}_actual"]
                    == merged[f"{column}_expected"]
                ).all(),
                f"Mismatch in {column}",
            )

        numeric_columns = [
            "total_sales",
            "total_profit",
            "avg_discount_pct",
            "loss_making_lines_pct",
            "profit_margin_pct",
        ]

        for column in numeric_columns:
            with self.subTest(column=column):
                self.assertTrue(
                    np.allclose(
                        merged[f"{column}_actual"],
                        merged[f"{column}_expected"],
                        atol=0.025,
                    ),
                    f"Mismatch in {column}",
                )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from .analytics import (
    average_discount,
    average_profit,
    monthly_sales,
    sales_by_category,
    sales_by_region,
    sales_by_segment,
    sales_by_state,
    top_n_products_by_sales,
    total_quantity_sold,
    total_sales,
)
from .models import SaleRecord
from .reader import read_sales_csv


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _filter_by_month(records: Iterable[SaleRecord], month: str | None) -> List[SaleRecord]:
    if not month:
        return list(records)
    return [
        record
        for record in records
        if record.order_date and record.order_date.strftime("%Y-%m") == month
    ]


def run_reports(records: Iterable[SaleRecord], *, top_n: int = 5, month: str | None = None) -> None:
    """Compute and print all analytics for the provided records."""
    record_list = _filter_by_month(records, month)

    def log(message: str) -> None:
        print(f"[SalesAnalysis] {message}")

    if not record_list:
        log(f"No records found for month filter '{month}'." if month else "Dataset is empty.")
        return

    log("==== Aggregate Metrics ====")
    log(f"Total sales: {_format_currency(total_sales(record_list))}")
    log(f"Total quantity sold: {total_quantity_sold(record_list)} units")
    log(f"Average discount: {average_discount(record_list):.2%}")
    log(f"Average profit: {_format_currency(average_profit(record_list))}")

    log("==== Grouped Views ====")
    log(f"Sales by region: {sales_by_region(record_list)}")
    log(f"Sales by category: {sales_by_category(record_list)}")
    log(f"Sales by segment: {sales_by_segment(record_list)}")
    log(f"Sales by state (top 5 shown): {dict(sorted(sales_by_state(record_list).items(), key=lambda kv: kv[1], reverse=True)[:5])}")

    log("==== Rankings & Trends ====")
    log(f"Top {top_n} products by sales: {top_n_products_by_sales(record_list, top_n)}")
    log(f"Monthly sales (YYYY-MM): {monthly_sales(record_list)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales analytics runner")
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="number of top products to display in the rankings",
    )
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="optional YYYY-MM filter (e.g., 2024-01) applied before aggregation",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "data" / "sales_sample.csv"
    print(f"[SalesAnalysis] Loading dataset from {csv_path}")
    records = read_sales_csv(csv_path)
    print(
        f"[SalesAnalysis] Loaded {len(records)} rows; generating analytics log..."
        + (f" filtered by month={args.month}" if args.month else "")
        + "\n"
    )
    run_reports(records, top_n=max(1, args.top_n), month=args.month)


if __name__ == "__main__":
    main()


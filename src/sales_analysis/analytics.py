from __future__ import annotations

from collections import defaultdict
from itertools import groupby
from typing import Dict, Iterable, List, Tuple

from .models import SaleRecord


def total_sales(records: Iterable[SaleRecord]) -> float:
    """Return the total sales revenue."""
    return sum(record.sales for record in records)


def total_quantity_sold(records: Iterable[SaleRecord]) -> int:
    """Return the total quantity sold."""
    return sum(record.quantity for record in records)


def average_discount(records: Iterable[SaleRecord]) -> float:
    """Return the mean discount across all records."""
    discounts = [record.discount for record in records]
    return sum(discounts) / len(discounts) if discounts else 0.0


def average_profit(records: Iterable[SaleRecord]) -> float:
    """Return the mean profit across all records."""
    profits = [record.profit for record in records]
    return sum(profits) / len(profits) if profits else 0.0


def sales_by_region(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """Aggregate sales revenue per region."""
    totals: Dict[str, float] = defaultdict(float)
    for record in records:
        totals[record.region] += record.sales
    return dict(totals)


def sales_by_category(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """Aggregate sales revenue per product category."""
    totals: Dict[str, float] = defaultdict(float)
    for record in records:
        totals[record.category] += record.sales
    return dict(totals)


def sales_by_segment(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """Aggregate sales revenue per customer segment."""
    totals: Dict[str, float] = defaultdict(float)
    for record in records:
        totals[record.segment] += record.sales
    return dict(totals)


def sales_by_state(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """Aggregate sales revenue per state."""
    totals: Dict[str, float] = defaultdict(float)
    for record in records:
        totals[record.state] += record.sales
    return dict(totals)


def top_n_products_by_sales(records: Iterable[SaleRecord], n: int) -> List[Tuple[str, float]]:
    """Return the top N products ranked by sales."""
    if n <= 0:
        return []
    totals = defaultdict(float)
    for record in records:
        totals[record.product_name] += record.sales
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return ranked[:n]


def monthly_sales(records: Iterable[SaleRecord]) -> Dict[str, float]:
    """Return sales aggregated per calendar month (YYYY-MM)."""
    dated_records = [rec for rec in records if rec.order_date is not None]
    sorted_records = sorted(dated_records, key=lambda rec: rec.order_date)  # type: ignore[arg-type]
    monthly_totals = (
        (month, sum(entry.sales for entry in group))
        for month, group in groupby(
            sorted_records,
            key=lambda rec: rec.order_date.strftime("%Y-%m")  # type: ignore[union-attr]
        )
    )
    return dict(monthly_totals)


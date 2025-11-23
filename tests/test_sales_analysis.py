from __future__ import annotations

from datetime import date

from src.sales_analysis.analytics import (
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
from src.sales_analysis.models import SaleRecord


def _make_record(**overrides: object) -> SaleRecord:
    base = {
        "row_id": "1",
        "order_id": "CA-2019-100001",
        "order_date": date(2019, 1, 3),
        "ship_date": date(2019, 1, 5),
        "ship_mode": "Standard Class",
        "customer_id": "CG-12500",
        "customer_name": "Carey Grant",
        "segment": "Consumer",
        "country": "United States",
        "city": "Austin",
        "state": "Texas",
        "postal_code": "73301",
        "region": "Central",
        "product_id": "OFF-PA-10000174",
        "category": "Office Supplies",
        "sub_category": "Paper",
        "product_name": "Xerox 225",
        "sales": 100.0,
        "quantity": 2,
        "discount": 0.1,
        "profit": 20.0,
    }
    base.update(overrides)
    return SaleRecord(**base)


def _sample_records() -> list[SaleRecord]:
    return [
        _make_record(row_id="1", product_name="Xerox 225", sales=200.0, region="Central"),
        _make_record(
            row_id="2",
            product_name="Staples",
            sales=150.0,
            region="East",
            category="Office Supplies",
            segment="Corporate",
            state="New York",
            quantity=5,
            discount=0.2,
            profit=40.0,
        ),
        _make_record(
            row_id="3",
            product_name="Office Chair",
            sales=300.0,
            region="Central",
            category="Furniture",
            segment="Consumer",
            state="Texas",
            quantity=3,
            discount=0.05,
            profit=60.0,
        ),
    ]


def test_total_sales() -> None:
    records = _sample_records()
    assert total_sales(records) == 650.0


def test_total_quantity_sold() -> None:
    records = _sample_records()
    assert total_quantity_sold(records) == 10


def test_average_discount_and_profit_handle_empty_list() -> None:
    assert average_discount([]) == 0.0
    assert average_profit([]) == 0.0


def test_average_discount_and_profit_non_empty() -> None:
    records = _sample_records()
    assert average_discount(records) == sum(r.discount for r in records) / len(records)
    assert average_profit(records) == sum(r.profit for r in records) / len(records)


def test_sales_groupings() -> None:
    records = _sample_records()
    assert sales_by_region(records)["Central"] == 500.0
    assert sales_by_category(records)["Furniture"] == 300.0
    assert sales_by_segment(records)["Corporate"] == 150.0
    assert sales_by_state(records)["Texas"] == 500.0


def test_top_n_products_by_sales() -> None:
    records = _sample_records()
    top_two = top_n_products_by_sales(records, 2)
    assert top_two[0][1] >= top_two[1][1]
    assert top_n_products_by_sales(records, 0) == []


def test_monthly_sales() -> None:
    records = _sample_records()
    assert monthly_sales(records) == {"2019-01": 650.0}


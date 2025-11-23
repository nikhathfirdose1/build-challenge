from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

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
from src.sales_analysis.reader import read_sales_csv


def _make_record(**overrides: object) -> SaleRecord:
    """Fabricate a SaleRecord, allowing overrides for individual fields."""
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
    """Return a deterministic mini dataset for analytics unit tests."""
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
    """total_sales should return the sum of every record's amount."""
    records = _sample_records()
    assert total_sales(records) == 650.0


def test_total_quantity_sold() -> None:
    """total_quantity_sold aggregates the quantity field."""
    records = _sample_records()
    assert total_quantity_sold(records) == 10


def test_average_discount_and_profit_handle_empty_list() -> None:
    """Average helpers must return zero when provided an empty iterable."""
    assert average_discount([]) == 0.0
    assert average_profit([]) == 0.0


def test_average_discount_and_profit_non_empty() -> None:
    """Average helpers compute the arithmetic mean for populated data."""
    records = _sample_records()
    assert average_discount(records) == sum(r.discount for r in records) / len(records)
    assert average_profit(records) == sum(r.profit for r in records) / len(records)


def test_sales_groupings() -> None:
    """Grouping helpers should bucket revenue by region/category/segment/state."""
    records = _sample_records()
    assert sales_by_region(records)["Central"] == 500.0
    assert sales_by_category(records)["Furniture"] == 300.0
    assert sales_by_segment(records)["Corporate"] == 150.0
    assert sales_by_state(records)["Texas"] == 500.0


def test_top_n_products_by_sales() -> None:
    """top_n_products_by_sales returns ranked tuples and handles zero limit."""
    records = _sample_records()
    top_two = top_n_products_by_sales(records, 2)
    assert top_two[0][1] >= top_two[1][1]
    assert top_n_products_by_sales(records, 0) == []


def test_monthly_sales() -> None:
    """monthly_sales buckets revenue into YYYY-MM keys."""
    records = _sample_records()
    assert monthly_sales(records) == {"2019-01": 650.0}


def test_read_sales_csv_handles_bom_and_missing_dates(tmp_path: Path) -> None:
    """Integration test for the CSV reader's BOM stripping and date parsing."""
    header = "\ufeffRow ID,Order ID,Order Date,Ship Date,Ship Mode,Customer ID,Customer Name,Segment,Country,City,State,Postal Code,Region,Product ID,Category,Sub-Category,Product Name,Sales,Quantity,Discount,Profit\n"
    row_one = "1,CA-2019-0001,,03/01/2019,Standard Class,C1,Carol,Consumer,United States,Seattle,Washington,98101,West,OFF-PA-1,Office Supplies,Paper,Paper A,100.0,2,0.1,30.0\n"
    row_two = "2,CA-2019-0002,03/15/2019,03/16/2019,Second Class,C2,Cameron,Corporate,United States,Denver,Colorado,80014,West,TEC-PH-1,Technology,Phones,Phone B,250.5,1,0,70.25\n"
    path = tmp_path / "sample.csv"
    path.write_text(header + row_one + row_two, encoding="utf-8")

    records = read_sales_csv(path)
    assert len(records) == 2
    first, second = records
    assert first.order_date is None
    assert first.ship_date == date(2019, 3, 1)
    assert second.order_date == date(2019, 3, 15)
    assert second.ship_date == date(2019, 3, 16)
    assert second.sales == pytest.approx(250.5)
    assert first.quantity == 2


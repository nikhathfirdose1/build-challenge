from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .models import SaleRecord

PathLike = Union[str, Path]
BOM = "\ufeff"
DATE_FORMAT = "%m/%d/%y"


def _parse_float(raw: str) -> float:
    return float(raw) if raw else 0.0


def _parse_int(raw: str) -> int:
    return int(float(raw)) if raw else 0


def _parse_date(raw: str) -> Optional[date]:
    cleaned = raw.strip()
    if not cleaned:
        return None
    # Support both two-digit and four-digit years.
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {raw}")


def read_sales_csv(path: PathLike) -> List[SaleRecord]:
    """Load sale records from the provided CSV file."""
    csv_path = Path(path)
    records: List[SaleRecord] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader: Iterable[dict[str, str]] = csv.DictReader(handle)
        for row in reader:
            if not row:
                continue
            normalized = {key.lstrip(BOM): value for key, value in row.items()}
            records.append(
                SaleRecord(
                    row_id=normalized["Row ID"],
                    order_id=normalized["Order ID"],
                    order_date=_parse_date(normalized["Order Date"]),
                    ship_date=_parse_date(normalized["Ship Date"]),
                    ship_mode=normalized["Ship Mode"],
                    customer_id=normalized["Customer ID"],
                    customer_name=normalized["Customer Name"],
                    segment=normalized["Segment"],
                    country=normalized["Country"],
                    city=normalized["City"],
                    state=normalized["State"],
                    postal_code=normalized["Postal Code"],
                    region=normalized["Region"],
                    product_id=normalized["Product ID"],
                    category=normalized["Category"],
                    sub_category=normalized["Sub-Category"],
                    product_name=normalized["Product Name"],
                    sales=_parse_float(normalized["Sales"]),
                    quantity=_parse_int(normalized["Quantity"]),
                    discount=_parse_float(normalized["Discount"]),
                    profit=_parse_float(normalized["Profit"]),
                )
            )
    return records


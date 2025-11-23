from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class SaleRecord:
    """Strongly typed representation of a single sale row."""

    row_id: str
    order_id: str
    order_date: Optional[date]
    ship_date: Optional[date]
    ship_mode: str
    customer_id: str
    customer_name: str
    segment: str
    country: str
    city: str
    state: str
    postal_code: str
    region: str
    product_id: str
    category: str
    sub_category: str
    product_name: str
    sales: float
    quantity: int
    discount: float
    profit: float


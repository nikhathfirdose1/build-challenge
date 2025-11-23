"""Sales CSV analysis toolkit."""

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

__all__ = [
    "SaleRecord",
    "read_sales_csv",
    "total_sales",
    "total_quantity_sold",
    "average_discount",
    "average_profit",
    "sales_by_region",
    "sales_by_category",
    "sales_by_segment",
    "sales_by_state",
    "top_n_products_by_sales",
    "monthly_sales",
]


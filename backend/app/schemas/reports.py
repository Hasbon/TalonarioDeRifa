from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_numbers: int
    available: int
    assigned: int
    total_sales: int
    total_received: int
    total_partial_payments_sum: int
    total_outstanding: int
    customers_count: int
    overdue_commitments: int


class SellerSalesReport(BaseModel):
    seller_id: str
    seller_name: str
    sales_count: int
    received: int
    outstanding: int

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.enums import CommercialStatus, PaymentRecordStatus, PaymentStatusSale
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.sale import Sale
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.reports import DashboardStats, SellerSalesReport
from app.utils.money import confirmed_total


def dashboard_stats(db: Session) -> DashboardStats:
    total_numbers = db.query(Ticket).count()
    assigned = (
        db.query(Sale)
        .filter(Sale.commercial_status == CommercialStatus.ACTIVE)
        .count()
    )
    available = total_numbers - assigned

    active_sales = (
        db.query(Sale)
        .options(joinedload(Sale.payments))
        .filter(Sale.commercial_status == CommercialStatus.ACTIVE)
        .all()
    )
    total_received = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == PaymentRecordStatus.CONFIRMED)
        .scalar()
    )
    total_outstanding = 0
    partial_sum = 0
    for s in active_sales:
        paid = confirmed_total(list(s.payments))
        bal = s.ticket_price - paid
        if bal > 0:
            total_outstanding += bal
        if s.payment_status == PaymentStatusSale.PARTIAL:
            partial_sum += paid

    customers_count = db.query(Customer).count()
    today = date.today()
    overdue = (
        db.query(Sale)
        .filter(
            Sale.commercial_status == CommercialStatus.ACTIVE,
            Sale.payment_status != PaymentStatusSale.PAID,
            Sale.payment_due_date.isnot(None),
            Sale.payment_due_date < today,
        )
        .count()
    )

    return DashboardStats(
        total_numbers=total_numbers,
        available=available,
        assigned=assigned,
        total_sales=assigned,
        total_received=int(total_received or 0),
        total_partial_payments_sum=partial_sum,
        total_outstanding=total_outstanding,
        customers_count=customers_count,
        overdue_commitments=overdue,
    )


def sales_by_seller(db: Session) -> list[SellerSalesReport]:
    sellers = db.query(User).all()
    reports: list[SellerSalesReport] = []
    for seller in sellers:
        sales = (
            db.query(Sale)
            .options(joinedload(Sale.payments))
            .filter(Sale.seller_id == seller.id, Sale.commercial_status == CommercialStatus.ACTIVE)
            .all()
        )
        received = 0
        outstanding = 0
        for s in sales:
            paid = confirmed_total(list(s.payments))
            received += paid
            outstanding += max(0, s.ticket_price - paid)
        reports.append(
            SellerSalesReport(
                seller_id=seller.id,
                seller_name=seller.full_name,
                sales_count=len(sales),
                received=received,
                outstanding=outstanding,
            )
        )
    return reports

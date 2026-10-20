from app.core.enums import PaymentRecordStatus, PaymentStatusSale
from app.models.payment import Payment
from app.models.sale import Sale


def confirmed_total(payments: list[Payment]) -> int:
    return sum(p.amount for p in payments if p.status == PaymentRecordStatus.CONFIRMED)


def compute_balance(sale: Sale) -> int:
    return sale.ticket_price - confirmed_total(list(sale.payments))


def compute_payment_status(sale: Sale) -> PaymentStatusSale:
    paid = confirmed_total(list(sale.payments))
    if paid <= 0:
        return PaymentStatusSale.UNPAID
    if paid >= sale.ticket_price:
        return PaymentStatusSale.PAID
    return PaymentStatusSale.PARTIAL

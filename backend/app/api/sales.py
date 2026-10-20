from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.sale import SaleCancel, SaleCreate, SaleOut, SaleUpdate, PaymentCreate, PaymentOut
from app.security.deps import require_admin, require_seller_or_admin
from app.services import sales as sales_service

router = APIRouter()


@router.get("", response_model=list[SaleOut])
def list_sales(
    number_code: str | None = None,
    customer_name: str | None = None,
    phone: str | None = None,
    seller_id: str | None = None,
    payment_status: str | None = None,
    commercial_status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.list_sales(
        db,
        user,
        number_code=number_code,
        customer_name=customer_name,
        phone=phone,
        seller_id=seller_id,
        payment_status=payment_status,
        commercial_status=commercial_status,
    )


@router.post("", response_model=SaleOut, status_code=201)
def create_sale(
    body: SaleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.create_sale(db, body, user)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.get_sale(db, sale_id, user)


@router.patch("/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: str,
    body: SaleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.update_sale(db, sale_id, body, user)


@router.post("/{sale_id}/cancel", response_model=SaleOut)
def cancel_sale(
    sale_id: str,
    body: SaleCancel,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return sales_service.cancel_sale(db, sale_id, body, user)


@router.post("/{sale_id}/payments", response_model=PaymentOut, status_code=201)
def add_payment(
    sale_id: str,
    body: PaymentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.add_payment(
        db,
        sale_id,
        body.amount,
        body.payment_method,
        body.payment_reference,
        body.confirm,
        user,
        body.notes,
    )


@router.get("/{sale_id}/payments", response_model=list[PaymentOut])
def list_payments(
    sale_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    sale = sales_service.get_sale(db, sale_id, user)
    return sale.payments

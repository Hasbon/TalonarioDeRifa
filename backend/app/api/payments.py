from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.sale import PaymentOut
from app.security.deps import require_admin, require_seller_or_admin
from app.services import sales as sales_service

router = APIRouter()


@router.post("/payments/{payment_id}/confirm", response_model=PaymentOut)
def confirm_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_seller_or_admin),
):
    return sales_service.confirm_payment(db, payment_id, user)


@router.post("/payments/{payment_id}/void", response_model=PaymentOut)
def void_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return sales_service.void_payment(db, payment_id, user)

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.enums import CommercialStatus, PaymentStatusSale, UserRole
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.raffle import Raffle
from app.models.sale import Sale
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.schemas.raffle import PublicRaffleOut, RaffleUpdate
from app.schemas.reports import DashboardStats, SellerSalesReport
from app.security.deps import require_admin, require_seller_or_admin
from app.security.passwords import hash_password
from app.services.audit import write_audit
from app.services import reports as reports_service
from app.utils.money import confirmed_total

router = APIRouter()


@router.get("/raffle", response_model=PublicRaffleOut)
def get_raffle(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")
    return PublicRaffleOut.model_validate(raffle)


@router.put("/raffle", response_model=PublicRaffleOut)
def update_raffle(
    body: RaffleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")

    data = body.model_dump(exclude_none=True)
    price_reason = data.pop("price_change_reason", None)
    if "ticket_price" in data and data["ticket_price"] != raffle.ticket_price:
        if not price_reason:
            raise HTTPException(
                status_code=400,
                detail="Debe indicar price_change_reason para modificar el precio",
            )
        write_audit(
            db,
            user_id=user.id,
            action="raffle.price_change",
            entity_type="raffle",
            entity_id=raffle.id,
            previous_values={"ticket_price": raffle.ticket_price},
            new_values={"ticket_price": data["ticket_price"]},
            reason=price_reason,
        )

    prev = {k: getattr(raffle, k) for k in data if hasattr(raffle, k)}
    for k, v in data.items():
        setattr(raffle, k, v)

    write_audit(
        db,
        user_id=user.id,
        action="raffle.update",
        entity_type="raffle",
        entity_id=raffle.id,
        previous_values={k: str(v) for k, v in prev.items()},
        new_values={k: str(v) for k, v in data.items()},
    )
    db.commit()
    db.refresh(raffle)
    return PublicRaffleOut.model_validate(raffle)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    return [UserOut.model_validate(u) for u in db.query(User).order_by(User.username).all()]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    new_user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        is_active=True,
    )
    db.add(new_user)
    write_audit(
        db,
        user_id=user.id,
        action="user.create",
        entity_type="user",
        entity_id=None,
        new_values={"username": body.username, "role": body.role.value},
    )
    db.commit()
    db.refresh(new_user)
    return UserOut.model_validate(new_user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = body.model_dump(exclude_none=True)
    if "password" in data:
        target.password_hash = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(target, k, v)
    write_audit(
        db,
        user_id=admin.id,
        action="user.update",
        entity_type="user",
        entity_id=target.id,
        new_values={k: str(v) for k, v in data.items()},
    )
    db.commit()
    db.refresh(target)
    return UserOut.model_validate(target)


@router.get("/reports", response_model=DashboardStats)
def reports(db: Session = Depends(get_db), user: User = Depends(require_seller_or_admin)):
    return reports_service.dashboard_stats(db)


@router.get("/reports/by-seller", response_model=list[SellerSalesReport])
def reports_by_seller(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    return reports_service.sales_by_seller(db)


@router.get("/reports/export.csv")
def export_csv(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    sales = (
        db.query(Sale)
        .filter(Sale.commercial_status == CommercialStatus.ACTIVE)
        .all()
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "sale_id",
            "number_code",
            "customer",
            "phone",
            "seller",
            "ticket_price",
            "paid",
            "balance",
            "payment_status",
            "due_date",
        ]
    )
    for s in sales:
        paid = confirmed_total(list(s.payments))
        writer.writerow(
            [
                s.id,
                s.ticket.number_code,
                s.customer.full_name,
                s.customer.phone,
                s.seller.full_name,
                s.ticket_price,
                paid,
                s.ticket_price - paid,
                s.payment_status.value,
                s.payment_due_date or "",
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_ventas.csv"},
    )


@router.get("/audit-logs")
def audit_logs(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
    limit: int = 100,
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "previous_values": log.previous_values,
            "new_values": log.new_values,
            "reason": log.reason,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/overdue")
def overdue_commitments(db: Session = Depends(get_db), user: User = Depends(require_seller_or_admin)):
    today = date.today()
    q = db.query(Sale).filter(
        Sale.commercial_status == CommercialStatus.ACTIVE,
        Sale.payment_status != PaymentStatusSale.PAID,
        Sale.payment_due_date.isnot(None),
        Sale.payment_due_date < today,
    )
    if user.role == UserRole.SELLER:
        q = q.filter(Sale.seller_id == user.id)
    sales = q.all()
    return [
        {
            "sale_id": s.id,
            "number_code": s.ticket.number_code,
            "customer": s.customer.full_name,
            "phone": s.customer.phone,
            "balance": s.ticket_price - confirmed_total(list(s.payments)),
            "payment_due_date": s.payment_due_date.isoformat(),
        }
        for s in sales
    ]

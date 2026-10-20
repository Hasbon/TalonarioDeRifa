from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.enums import CommercialStatus, PaymentRecordStatus, PaymentStatusSale, UserRole
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.raffle import Raffle
from app.models.sale import Sale
from app.models.ticket import Ticket
from app.models.ticket_token import TicketPublicToken
from app.models.user import User
from app.schemas.sale import (
    PaymentOut,
    SaleCancel,
    SaleCreate,
    SaleOut,
    SaleUpdate,
    CustomerOut,
    SellerBrief,
)
from app.services.audit import write_audit
from app.utils.money import compute_balance, compute_payment_status, confirmed_total
from app.utils.phone import normalize_phone


def get_active_raffle(db: Session) -> Raffle:
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="No hay rifa configurada")
    return raffle


def _sale_to_out(sale: Sale, public_token: str | None = None) -> SaleOut:
    total = confirmed_total(list(sale.payments))
    token = public_token
    if token is None:
        active = next((t for t in sale.ticket.public_tokens if t.is_active and t.sale_id == sale.id), None)
        token = active.public_token if active else None
    return SaleOut(
        id=sale.id,
        ticket_id=sale.ticket_id,
        number_code=sale.ticket.number_code,
        customer=CustomerOut.model_validate(sale.customer),
        seller=SellerBrief.model_validate(sale.seller),
        ticket_price=sale.ticket_price,
        commercial_status=sale.commercial_status,
        payment_status=sale.payment_status,
        total_paid=total,
        balance_due=sale.ticket_price - total,
        payment_due_date=sale.payment_due_date,
        internal_notes=sale.internal_notes,
        assigned_at=sale.assigned_at,
        cancelled_at=sale.cancelled_at,
        cancellation_reason=sale.cancellation_reason,
        public_token=token,
        payments=[PaymentOut.model_validate(p) for p in sale.payments],
    )


def create_sale(db: Session, data: SaleCreate, seller: User) -> SaleOut:
    raffle = get_active_raffle(db)
    number_code = data.number_code

    ticket = (
        db.query(Ticket)
        .filter(Ticket.raffle_id == raffle.id, Ticket.number_code == number_code)
        .with_for_update()
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Número no encontrado")

    active = (
        db.query(Sale)
        .filter(Sale.ticket_id == ticket.id, Sale.commercial_status == CommercialStatus.ACTIVE)
        .first()
    )
    if active:
        raise HTTPException(status_code=409, detail="El número ya tiene una asignación activa")

    if data.initial_payment > raffle.ticket_price:
        raise HTTPException(status_code=400, detail="El abono inicial no puede superar el precio")

    try:
        phone = normalize_phone(data.customer_phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    customer = db.query(Customer).filter(Customer.phone == phone).first()
    if customer:
        customer.full_name = data.customer_full_name.strip()
    else:
        customer = Customer(full_name=data.customer_full_name.strip(), phone=phone)
        db.add(customer)
        db.flush()

    sale = Sale(
        ticket_id=ticket.id,
        customer_id=customer.id,
        seller_id=seller.id,
        ticket_price=raffle.ticket_price,
        commercial_status=CommercialStatus.ACTIVE,
        payment_status=PaymentStatusSale.UNPAID,
        payment_due_date=data.payment_due_date,
        internal_notes=data.internal_notes,
        assigned_at=datetime.now(timezone.utc),
    )
    db.add(sale)
    db.flush()

    if data.initial_payment > 0:
        payment = Payment(
            sale_id=sale.id,
            amount=data.initial_payment,
            payment_method=data.payment_method or "efectivo",
            payment_reference=data.payment_reference,
            status=PaymentRecordStatus.CONFIRMED,
            registered_by=seller.id,
        )
        db.add(payment)
        db.flush()
        sale.payment_status = compute_payment_status(sale)

    token = TicketPublicToken(ticket_id=ticket.id, sale_id=sale.id, is_active=True)
    db.add(token)
    public_token_value = token.public_token
    sale_id = sale.id

    write_audit(
        db,
        user_id=seller.id,
        action="sale.create",
        entity_type="sale",
        entity_id=sale_id,
        new_values={
            "number_code": number_code,
            "customer_id": customer.id,
            "ticket_price": sale.ticket_price,
            "initial_payment": data.initial_payment,
        },
    )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El número ya fue asignado por otra operación concurrente",
        ) from exc

    sale = (
        db.query(Sale)
        .options(
            joinedload(Sale.customer),
            joinedload(Sale.seller),
            joinedload(Sale.payments),
            joinedload(Sale.ticket).joinedload(Ticket.public_tokens),
        )
        .filter(Sale.id == sale_id)
        .one()
    )
    return _sale_to_out(sale, public_token=public_token_value)


def list_sales(
    db: Session,
    user: User,
    *,
    number_code: str | None = None,
    customer_name: str | None = None,
    phone: str | None = None,
    seller_id: str | None = None,
    payment_status: str | None = None,
    commercial_status: str | None = None,
) -> list[SaleOut]:
    q = db.query(Sale).options(
        joinedload(Sale.customer),
        joinedload(Sale.seller),
        joinedload(Sale.payments),
        joinedload(Sale.ticket).joinedload(Ticket.public_tokens),
    )
    if user.role == UserRole.SELLER:
        q = q.filter(Sale.seller_id == user.id)
    elif seller_id:
        q = q.filter(Sale.seller_id == seller_id)

    if number_code:
        q = q.join(Ticket).filter(Ticket.number_code == number_code.zfill(2))
    if customer_name:
        q = q.join(Customer).filter(Customer.full_name.ilike(f"%{customer_name}%"))
    if phone:
        try:
            ph = normalize_phone(phone)
            q = q.join(Customer).filter(Customer.phone.contains(ph))
        except ValueError:
            pass
    if payment_status:
        q = q.filter(Sale.payment_status == payment_status)
    if commercial_status:
        q = q.filter(Sale.commercial_status == commercial_status)

    sales = q.order_by(Sale.assigned_at.desc()).all()
    return [_sale_to_out(s) for s in sales]


def get_sale(db: Session, sale_id: str, user: User) -> SaleOut:
    sale = (
        db.query(Sale)
        .options(
            joinedload(Sale.customer),
            joinedload(Sale.seller),
            joinedload(Sale.payments),
            joinedload(Sale.ticket).joinedload(Ticket.public_tokens),
        )
        .filter(Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if user.role == UserRole.SELLER and sale.seller_id != user.id:
        raise HTTPException(status_code=403, detail="No autorizado para esta venta")
    return _sale_to_out(sale)


def update_sale(db: Session, sale_id: str, data: SaleUpdate, user: User) -> SaleOut:
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if user.role == UserRole.SELLER and sale.seller_id != user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    if sale.commercial_status != CommercialStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="La venta no está activa")

    prev = {"payment_due_date": str(sale.payment_due_date), "internal_notes": sale.internal_notes}
    if data.payment_due_date is not None:
        sale.payment_due_date = data.payment_due_date
    if data.internal_notes is not None:
        sale.internal_notes = data.internal_notes
    write_audit(
        db,
        user_id=user.id,
        action="sale.update",
        entity_type="sale",
        entity_id=sale.id,
        previous_values=prev,
        new_values=data.model_dump(exclude_none=True),
    )
    db.commit()
    return get_sale(db, sale_id, user)


def cancel_sale(db: Session, sale_id: str, data: SaleCancel, admin: User) -> SaleOut:
    if admin.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo un administrador puede anular")

    sale = (
        db.query(Sale)
        .options(
            joinedload(Sale.customer),
            joinedload(Sale.seller),
            joinedload(Sale.payments),
            joinedload(Sale.ticket).joinedload(Ticket.public_tokens),
        )
        .filter(Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if sale.commercial_status != CommercialStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    sale.commercial_status = CommercialStatus.CANCELLED
    sale.cancelled_at = datetime.now(timezone.utc)
    sale.cancellation_reason = data.reason

    for tok in sale.ticket.public_tokens:
        if tok.is_active and tok.sale_id == sale.id:
            tok.is_active = False
            tok.revoked_at = datetime.now(timezone.utc)

    write_audit(
        db,
        user_id=admin.id,
        action="sale.cancel",
        entity_type="sale",
        entity_id=sale.id,
        reason=data.reason,
        new_values={"commercial_status": "cancelled", "number_code": sale.ticket.number_code},
    )
    db.commit()
    db.refresh(sale)
    return _sale_to_out(sale)


def add_payment(db: Session, sale_id: str, amount: int, method: str, reference: str | None, confirm: bool, user: User, notes: str | None = None) -> PaymentOut:
    sale = (
        db.query(Sale)
        .options(joinedload(Sale.payments))
        .filter(Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if user.role == UserRole.SELLER and sale.seller_id != user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    if sale.commercial_status != CommercialStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="La venta no está activa")

    balance = compute_balance(sale)
    if amount > balance and confirm:
        raise HTTPException(status_code=400, detail="El pago supera el saldo pendiente")

    payment = Payment(
        sale_id=sale.id,
        amount=amount,
        payment_method=method,
        payment_reference=reference,
        status=PaymentRecordStatus.CONFIRMED if confirm else PaymentRecordStatus.PENDING,
        registered_by=user.id,
        notes=notes,
    )
    db.add(payment)
    sale.payments.append(payment)
    db.flush()
    if confirm:
        db.refresh(sale, attribute_names=["payments"])
        sale.payment_status = compute_payment_status(sale)

    write_audit(
        db,
        user_id=user.id,
        action="payment.create",
        entity_type="payment",
        entity_id=payment.id,
        new_values={"amount": amount, "status": payment.status.value, "sale_id": sale.id},
    )
    db.commit()
    db.refresh(payment)
    return PaymentOut.model_validate(payment)


def confirm_payment(db: Session, payment_id: str, user: User) -> PaymentOut:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    sale = db.get(Sale, payment.sale_id)
    if user.role == UserRole.SELLER and sale and sale.seller_id != user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    if payment.status != PaymentRecordStatus.PENDING:
        raise HTTPException(status_code=400, detail="Solo se confirman pagos pendientes")

    balance = compute_balance(sale)  # type: ignore[arg-type]
    if payment.amount > balance:
        raise HTTPException(status_code=400, detail="El pago supera el saldo pendiente")

    payment.status = PaymentRecordStatus.CONFIRMED
    sale.payment_status = compute_payment_status(sale)  # type: ignore[arg-type]
    write_audit(
        db,
        user_id=user.id,
        action="payment.confirm",
        entity_type="payment",
        entity_id=payment.id,
    )
    db.commit()
    db.refresh(payment)
    return PaymentOut.model_validate(payment)


def void_payment(db: Session, payment_id: str, user: User) -> PaymentOut:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Solo un administrador puede anular pagos")
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if payment.status == PaymentRecordStatus.VOIDED:
        raise HTTPException(status_code=400, detail="El pago ya está anulado")

    payment.status = PaymentRecordStatus.VOIDED
    sale = (
        db.query(Sale).options(joinedload(Sale.payments)).filter(Sale.id == payment.sale_id).one()
    )
    sale.payment_status = compute_payment_status(sale)
    write_audit(
        db,
        user_id=user.id,
        action="payment.void",
        entity_type="payment",
        entity_id=payment.id,
    )
    db.commit()
    db.refresh(payment)
    return PaymentOut.model_validate(payment)

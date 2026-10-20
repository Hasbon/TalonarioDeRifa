from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.enums import CommercialStatus, PaymentStatusSale
from app.models.raffle import Raffle
from app.models.sale import Sale
from app.models.ticket import Ticket
from app.models.ticket_token import TicketPublicToken
from app.schemas.boleta import PublicBoletaOut
from app.schemas.raffle import PublicRaffleOut, PublicTicketDetailOut, PublicTicketOut


def get_public_raffle(db: Session) -> PublicRaffleOut:
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")
    return PublicRaffleOut.model_validate(raffle)


def list_public_tickets(db: Session) -> list[PublicTicketOut]:
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")

    tickets = (
        db.query(Ticket)
        .filter(Ticket.raffle_id == raffle.id)
        .order_by(Ticket.number_code)
        .all()
    )
    active_ticket_ids = {
        s.ticket_id
        for s in db.query(Sale.ticket_id)
        .filter(Sale.commercial_status == CommercialStatus.ACTIVE)
        .all()
    }
    return [
        PublicTicketOut(number_code=t.number_code, available=t.id not in active_ticket_ids)
        for t in tickets
    ]


def get_public_ticket(db: Session, number_code: str) -> PublicTicketDetailOut:
    code = number_code.zfill(2)
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")
    ticket = (
        db.query(Ticket)
        .filter(Ticket.raffle_id == raffle.id, Ticket.number_code == code)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Número no encontrado")
    active = (
        db.query(Sale)
        .filter(Sale.ticket_id == ticket.id, Sale.commercial_status == CommercialStatus.ACTIVE)
        .first()
    )
    return PublicTicketDetailOut(
        number_code=ticket.number_code,
        available=active is None,
        raffle_name=raffle.name,
    )


def get_public_boleta(db: Session, public_token: str) -> PublicBoletaOut:
    token = (
        db.query(TicketPublicToken)
        .options(joinedload(TicketPublicToken.ticket).joinedload(Ticket.raffle))
        .filter(TicketPublicToken.public_token == public_token)
        .first()
    )
    if not token:
        raise HTTPException(status_code=404, detail="Boleta no encontrada")

    raffle = token.ticket.raffle
    sale = None
    if token.sale_id:
        sale = db.get(Sale, token.sale_id)

    if not token.is_active or (sale and sale.commercial_status == CommercialStatus.CANCELLED):
        validity = "revoked"
        assignment_status = "cancelled"
    elif sale and sale.commercial_status == CommercialStatus.ACTIVE:
        validity = "valid"
        assignment_status = "active"
    else:
        validity = "unknown"
        assignment_status = "none"

    financial_label = None
    if sale and sale.commercial_status == CommercialStatus.ACTIVE:
        if sale.payment_status == PaymentStatusSale.PAID:
            financial_label = "Pagada"
        elif sale.payment_status == PaymentStatusSale.PARTIAL:
            financial_label = "Abono parcial"
        else:
            financial_label = "Pendiente de pago"

    return PublicBoletaOut(
        raffle_name=raffle.name,
        number_code=token.ticket.number_code,
        validity=validity,
        assignment_status=assignment_status,
        draw_date=raffle.draw_date,
        delivery_datetime=raffle.delivery_datetime,
        primary_prize=raffle.primary_prize,
        alternative_prize_amount=raffle.alternative_prize_amount,
        ticket_price=raffle.ticket_price,
        public_token=token.public_token,
        financial_label=financial_label if validity == "valid" else None,
    )

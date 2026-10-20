from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.enums import CommercialStatus, VerificationStatus
from app.models.lottery_result import LotteryResult
from app.models.raffle import Raffle
from app.models.sale import Sale
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.lottery import LotteryResultCreate, LotteryResultOut
from app.services.audit import write_audit
from app.utils.winner import derive_winner_code


def _to_out(db: Session, result: LotteryResult) -> LotteryResultOut:
    has_assignment = None
    winner_name = None
    ticket = (
        db.query(Ticket)
        .filter(Ticket.raffle_id == result.raffle_id, Ticket.number_code == result.derived_winner_code)
        .first()
    )
    if ticket:
        sale = (
            db.query(Sale)
            .options(joinedload(Sale.customer))
            .filter(Sale.ticket_id == ticket.id, Sale.commercial_status == CommercialStatus.ACTIVE)
            .first()
        )
        has_assignment = sale is not None
        if sale:
            winner_name = sale.customer.full_name

    return LotteryResultOut(
        id=result.id,
        raffle_id=result.raffle_id,
        lottery_name=result.lottery_name,
        draw_reference=result.draw_reference,
        draw_date=result.draw_date,
        winning_number=result.winning_number,
        derived_winner_code=result.derived_winner_code,
        official_source_url=result.official_source_url,
        verification_status=result.verification_status.value,
        verified_by=result.verified_by,
        verified_at=result.verified_at,
        notes=result.notes,
        created_at=result.created_at,
        has_active_assignment=has_assignment,
        winner_customer_name=winner_name
        if result.verification_status == VerificationStatus.CONFIRMED
        else None,
    )


def create_result(db: Session, data: LotteryResultCreate, admin: User) -> LotteryResultOut:
    raffle = db.query(Raffle).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Rifa no encontrada")
    try:
        code = derive_winner_code(data.winning_number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = LotteryResult(
        raffle_id=raffle.id,
        lottery_name=data.lottery_name,
        draw_reference=data.draw_reference,
        draw_date=data.draw_date,
        winning_number=data.winning_number,
        derived_winner_code=code,
        official_source_url=data.official_source_url,
        verification_status=VerificationStatus.DRAFT,
        notes=data.notes,
    )
    db.add(result)
    write_audit(
        db,
        user_id=admin.id,
        action="lottery_result.create",
        entity_type="lottery_result",
        entity_id=None,
        new_values={"winning_number": data.winning_number, "derived": code},
    )
    db.commit()
    db.refresh(result)
    write_audit(
        db,
        user_id=admin.id,
        action="lottery_result.created",
        entity_type="lottery_result",
        entity_id=result.id,
    )
    db.commit()
    return _to_out(db, result)


def confirm_result(db: Session, result_id: str, admin: User) -> LotteryResultOut:
    result = db.get(LotteryResult, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    if result.verification_status == VerificationStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="El resultado ya está confirmado")

    result.verification_status = VerificationStatus.CONFIRMED
    result.verified_by = admin.id
    result.verified_at = datetime.now(timezone.utc)

    write_audit(
        db,
        user_id=admin.id,
        action="lottery_result.confirm",
        entity_type="lottery_result",
        entity_id=result.id,
        new_values={
            "derived_winner_code": result.derived_winner_code,
            "winning_number": result.winning_number,
        },
    )
    db.commit()
    db.refresh(result)
    return _to_out(db, result)


def list_results(db: Session) -> list[LotteryResultOut]:
    results = db.query(LotteryResult).order_by(LotteryResult.created_at.desc()).all()
    return [_to_out(db, r) for r in results]

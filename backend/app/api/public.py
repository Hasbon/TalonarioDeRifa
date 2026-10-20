from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.boleta import PublicBoletaOut
from app.schemas.raffle import PublicRaffleOut, PublicTicketDetailOut, PublicTicketOut
from app.services import public as public_service

router = APIRouter()


@router.get("/raffle", response_model=PublicRaffleOut)
def public_raffle(db: Session = Depends(get_db)):
    return public_service.get_public_raffle(db)


@router.get("/tickets", response_model=list[PublicTicketOut])
def public_tickets(db: Session = Depends(get_db)):
    return public_service.list_public_tickets(db)


@router.get("/tickets/{number_code}", response_model=PublicTicketDetailOut)
def public_ticket(number_code: str, db: Session = Depends(get_db)):
    return public_service.get_public_ticket(db, number_code)


@router.get("/boletas/{public_token}", response_model=PublicBoletaOut)
def public_boleta(public_token: str, db: Session = Depends(get_db)):
    return public_service.get_public_boleta(db, public_token)

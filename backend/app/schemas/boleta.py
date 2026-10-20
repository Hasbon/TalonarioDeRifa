from datetime import date, datetime

from pydantic import BaseModel


class PublicBoletaOut(BaseModel):
    raffle_name: str
    number_code: str
    validity: str  # valid | revoked | unknown
    assignment_status: str  # active | cancelled | none
    draw_date: date
    delivery_datetime: datetime
    primary_prize: str
    alternative_prize_amount: int
    ticket_price: int
    public_token: str
    # Financial label without amounts for privacy on validation page:
    # only high-level "informativa" — no debts/phones
    financial_label: str | None = None

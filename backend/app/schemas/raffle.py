from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.enums import RaffleStatus


class PublicRaffleOut(BaseModel):
    id: str
    name: str
    description: str
    primary_prize: str
    alternative_prize_amount: int
    ticket_price: int
    draw_date: date
    delivery_datetime: datetime
    lottery_name: str
    lottery_draw_reference: str
    status: RaffleStatus
    public_contact: str
    public_rules: str
    privacy_notice: str
    logo_url: str | None = None

    model_config = {"from_attributes": True}


class RaffleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    primary_prize: str | None = None
    alternative_prize_amount: int | None = Field(default=None, ge=0)
    ticket_price: int | None = Field(default=None, ge=1)
    draw_date: date | None = None
    delivery_datetime: datetime | None = None
    lottery_name: str | None = None
    lottery_draw_reference: str | None = None
    status: RaffleStatus | None = None
    public_contact: str | None = None
    public_rules: str | None = None
    privacy_notice: str | None = None
    logo_url: str | None = None
    price_change_reason: str | None = Field(
        default=None,
        description="Obligatorio si se modifica ticket_price",
    )


class PublicTicketOut(BaseModel):
    number_code: str
    available: bool


class PublicTicketDetailOut(BaseModel):
    number_code: str
    available: bool
    raffle_name: str

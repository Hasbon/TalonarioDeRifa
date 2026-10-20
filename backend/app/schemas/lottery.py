from datetime import date, datetime

from pydantic import BaseModel, Field


class LotteryResultCreate(BaseModel):
    lottery_name: str = Field(min_length=2, max_length=200)
    draw_reference: str = Field(min_length=1, max_length=255)
    draw_date: date
    winning_number: str = Field(min_length=2, max_length=32)
    official_source_url: str = Field(min_length=5, max_length=500)
    notes: str | None = None


class LotteryResultOut(BaseModel):
    id: str
    raffle_id: str
    lottery_name: str
    draw_reference: str
    draw_date: date
    winning_number: str
    derived_winner_code: str
    official_source_url: str
    verification_status: str
    verified_by: str | None
    verified_at: datetime | None
    notes: str | None
    created_at: datetime
    has_active_assignment: bool | None = None
    winner_customer_name: str | None = None

    model_config = {"from_attributes": True}

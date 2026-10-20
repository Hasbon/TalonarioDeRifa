import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RaffleStatus
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Raffle(Base):
    __tablename__ = "raffles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    primary_prize: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_prize_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_price: Mapped[int] = mapped_column(Integer, nullable=False)
    draw_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    lottery_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lottery_draw_reference: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[RaffleStatus] = mapped_column(
        Enum(RaffleStatus), default=RaffleStatus.ACTIVE, nullable=False
    )
    public_contact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    public_rules: Mapped[str] = mapped_column(Text, nullable=False, default="")
    privacy_notice: Mapped[str] = mapped_column(Text, nullable=False, default="")
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    tickets = relationship("Ticket", back_populates="raffle")
    lottery_results = relationship("LotteryResult", back_populates="raffle")

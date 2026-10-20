import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (UniqueConstraint("raffle_id", "number_code", name="uq_raffle_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    raffle_id: Mapped[str] = mapped_column(String(36), ForeignKey("raffles.id"), nullable=False)
    number_code: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    raffle = relationship("Raffle", back_populates="tickets")
    sales = relationship("Sale", back_populates="ticket")
    public_tokens = relationship("TicketPublicToken", back_populates="ticket")

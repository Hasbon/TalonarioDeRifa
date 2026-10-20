import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import VerificationStatus
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LotteryResult(Base):
    __tablename__ = "lottery_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    raffle_id: Mapped[str] = mapped_column(String(36), ForeignKey("raffles.id"), nullable=False)
    lottery_name: Mapped[str] = mapped_column(String(200), nullable=False)
    draw_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    draw_date: Mapped[date] = mapped_column(Date, nullable=False)
    winning_number: Mapped[str] = mapped_column(String(32), nullable=False)
    derived_winner_code: Mapped[str] = mapped_column(String(2), nullable=False)
    official_source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.DRAFT, nullable=False
    )
    verified_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    raffle = relationship("Raffle", back_populates="lottery_results")

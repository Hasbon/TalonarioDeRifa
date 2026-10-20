import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CommercialStatus, PaymentStatusSale
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        Index(
            "uq_active_sale_per_ticket",
            "ticket_id",
            unique=True,
            postgresql_where=text("commercial_status = 'active'"),
            sqlite_where=text("commercial_status = 'active'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    ticket_id: Mapped[str] = mapped_column(String(36), ForeignKey("tickets.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    seller_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    ticket_price: Mapped[int] = mapped_column(Integer, nullable=False)
    commercial_status: Mapped[CommercialStatus] = mapped_column(
        Enum(CommercialStatus), default=CommercialStatus.ACTIVE, nullable=False
    )
    payment_status: Mapped[PaymentStatusSale] = mapped_column(
        Enum(PaymentStatusSale), default=PaymentStatusSale.UNPAID, nullable=False
    )
    payment_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    ticket = relationship("Ticket", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    seller = relationship("User", back_populates="sales", foreign_keys=[seller_id])
    payments = relationship("Payment", back_populates="sale", order_by="Payment.created_at")

"""Sync official raffle catalog fields in the local/dev database."""

from __future__ import annotations

from sqlalchemy import text

from app.db.base import Base
from app.db.seed import (
    DEFAULT_RULES,
    OFFICIAL_DRAW_DATE,
    OFFICIAL_LOTTERY_REF,
    OFFICIAL_TICKET_PRICE,
    _official_delivery_utc,
    ensure_raffle_and_tickets,
)
from app.db.session import SessionLocal, engine
import app.models  # noqa: F401


def main() -> int:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("UPDATE raffles SET status = lower(status) WHERE upper(status) = status"))

    db = SessionLocal()
    try:
        raffle = ensure_raffle_and_tickets(db)
        # Force catalog fields even if comparison failed earlier.
        raffle.draw_date = OFFICIAL_DRAW_DATE
        raffle.delivery_datetime = _official_delivery_utc()
        raffle.ticket_price = OFFICIAL_TICKET_PRICE
        raffle.lottery_draw_reference = OFFICIAL_LOTTERY_REF
        raffle.public_rules = DEFAULT_RULES
        db.commit()
        db.refresh(raffle)
        print(f"draw={raffle.draw_date}")
        print(f"delivery={raffle.delivery_datetime}")
        print(f"price={raffle.ticket_price}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

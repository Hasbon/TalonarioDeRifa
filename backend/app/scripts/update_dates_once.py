from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.db.session import SessionLocal
from app.models.raffle import Raffle

RULES = """REGLAMENTO DE LA RIFA

1. Se rifan 100 números del 00 al 99.
2. Precio de cada boleta: $30.000 COP (precio vigente al momento de la asignación).
3. Premio principal: un cerdo de 90 kilogramos y una garrafa de aguardiente.
4. Premio alternativo: $1.200.000 COP en efectivo, sujeto a las condiciones oficiales.
5. Fecha del sorteo: 22 de diciembre de 2026.
6. El número ganador corresponde a las dos últimas cifras del premio mayor de la Lotería de la Cruz Roja del sorteo previamente definido.
7. Entrega del premio: 23 de diciembre de 2026 a las 11:00 a. m., hora de Colombia (America/Bogota).
8. Boleta que no esté paga no juega. Solo participa en el sorteo la boleta cuyo valor total esté completamente pagado antes del sorteo. Un abono parcial reserva el número, pero no otorga derecho a reclamar el premio.
9. La asignación de un número lo reserva aunque el pago no esté completo. Solo se libera mediante anulación autorizada.
10. Antes de comercializar, verifique los requisitos legales aplicables en Colombia para rifas y juegos de suerte y azar.
11. Este software no constituye por sí solo una autorización oficial para operar la rifa.
"""


def main() -> None:
    db = SessionLocal()
    try:
        raffle = db.query(Raffle).first()
        if not raffle:
            raise SystemExit("No raffle")
        print("before", raffle.draw_date, raffle.delivery_datetime, raffle.ticket_price)
        raffle.draw_date = date(2026, 12, 22)
        raffle.delivery_datetime = datetime(
            2026, 12, 23, 11, 0, 0, tzinfo=ZoneInfo("America/Bogota")
        ).astimezone(timezone.utc)
        raffle.ticket_price = 30000
        raffle.lottery_name = "Lotería de la Cruz Roja"
        raffle.lottery_draw_reference = "Sorteo del 22 de diciembre de 2026 (premio mayor)"
        raffle.public_rules = RULES
        db.commit()
        print("after", raffle.draw_date, raffle.delivery_datetime, raffle.ticket_price)
    finally:
        db.close()


if __name__ == "__main__":
    main()

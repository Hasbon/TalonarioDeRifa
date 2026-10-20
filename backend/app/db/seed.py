from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.enums import RaffleStatus
from app.models.raffle import Raffle
from app.models.ticket import Ticket

DEFAULT_RULES = """REGLAMENTO DE LA RIFA

1. Se rifan 100 números del 00 al 99.
2. Precio de cada boleta: $35.000 COP (precio vigente al momento de la asignación).
3. Premio principal: un cerdo de 90 kilogramos y una garrafa de aguardiente.
4. Premio alternativo: $1.200.000 COP en efectivo, sujeto a las condiciones oficiales.
5. Fecha del sorteo: 30 de diciembre de 2026.
6. El número ganador corresponde a las dos últimas cifras del premio mayor de la Lotería del Valle del sorteo previamente definido.
7. Entrega del premio: 31 de diciembre de 2026 a las 10:00 a. m., hora de Colombia (America/Bogota).
8. La asignación de un número lo reserva aunque el pago no esté completo. Solo se libera mediante anulación autorizada.
9. Antes de comercializar, verifique los requisitos legales aplicables en Colombia para rifas y juegos de suerte y azar.
10. Este software no constituye por sí solo una autorización oficial para operar la rifa.
"""

DEFAULT_PRIVACY = """AVISO DE PRIVACIDAD

Los datos personales de compradores (nombre y teléfono) se recopilan únicamente para la gestión de la rifa, el seguimiento de pagos y la entrega del premio. No se publican en el tablero público ni en la validación por código QR. El tratamiento se realiza conforme a la Ley 1581 de 2012 (Habeas Data) de Colombia. Para consultas sobre sus datos, utilice el contacto público indicado.
"""


def ensure_raffle_and_tickets(db: Session) -> Raffle:
    raffle = db.query(Raffle).first()
    if raffle is None:
        bogota = ZoneInfo("America/Bogota")
        delivery = datetime(2026, 12, 31, 10, 0, 0, tzinfo=bogota)
        raffle = Raffle(
            name="Rifa Fin de Año 2026",
            description="Rifa digital de fin de año. 100 números del 00 al 99.",
            primary_prize="Un cerdo de 90 kilogramos y una garrafa de aguardiente",
            alternative_prize_amount=1_200_000,
            ticket_price=35_000,
            draw_date=date(2026, 12, 30),
            delivery_datetime=delivery.astimezone(timezone.utc),
            lottery_name="Lotería del Valle",
            lottery_draw_reference="Sorteo del 30 de diciembre de 2026 (premio mayor)",
            status=RaffleStatus.ACTIVE,
            public_contact="Contacto del organizador: configurar en panel de administración.",
            public_rules=DEFAULT_RULES,
            privacy_notice=DEFAULT_PRIVACY,
        )
        db.add(raffle)
        db.flush()

    existing = {t.number_code for t in raffle.tickets}
    for i in range(100):
        code = f"{i:02d}"
        if code not in existing:
            db.add(Ticket(raffle_id=raffle.id, number_code=code))
    db.commit()
    db.refresh(raffle)
    return raffle

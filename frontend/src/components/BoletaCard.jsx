import { forwardRef } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { granRifaFlyerUrl } from '../assets/raffleAssets';
import { formatCOP, formatDate, formatDateTime, paymentStatusLabel } from '../utils/format';
import './BoletaCard.css';

const BoletaCard = forwardRef(function BoletaCard({ sale, raffle }, ref) {
  const base = import.meta.env.VITE_PUBLIC_BASE_URL || window.location.origin;
  const url = `${base}/boleta/${sale.public_token}`;
  const paidLabel =
    sale.payment_status === 'paid'
      ? 'PAGADA'
      : `${paymentStatusLabel(sale.payment_status)} · Saldo ${formatCOP(sale.balance_due)}`;

  return (
    <article className="boleta-card" ref={ref}>
      <div className="boleta-card__band">
        <span>Boleta digital</span>
        <strong>{raffle?.name || 'Rifa Fin de Año 2026'}</strong>
      </div>
      <div className="boleta-card__number">{sale.number_code}</div>
      <div
        className="boleta-card__body"
        style={{ backgroundImage: `url(${granRifaFlyerUrl})` }}
      >
        <div className="boleta-card__panel">
          <p>
            <span>Comprador</span>
            <strong>{sale.customer.full_name}</strong>
          </p>
          <p>
            <span>Premio</span>
            <strong>{raffle?.primary_prize || 'Cerdo 90 kg + garrafa de aguardiente'}</strong>
          </p>
          <p>
            <span>Alternativa</span>
            <strong>{formatCOP(raffle?.alternative_prize_amount || 1200000)}</strong>
          </p>
          <p>
            <span>Precio</span>
            <strong>{formatCOP(sale.ticket_price)}</strong>
          </p>
          <p>
            <span>Sorteo</span>
            <strong>{formatDate(raffle?.draw_date || '2026-12-30')}</strong>
          </p>
          <p>
            <span>Entrega</span>
            <strong>{formatDateTime(raffle?.delivery_datetime)}</strong>
          </p>
        </div>
        <p className={`boleta-card__pay boleta-card__pay--${sale.payment_status}`}>
          {paidLabel}
        </p>
        <div className="boleta-card__qr">
          <QRCodeSVG value={url} size={128} level="M" includeMargin />
          <small>Escanee para validar</small>
        </div>
        <p className="boleta-card__id">ID: {sale.public_token?.slice(0, 12)}…</p>
        <p className="boleta-card__disclaimer">
          Esta imagen no confirma por sí sola el pago. Consulte el estado actual con el QR.
        </p>
      </div>
    </article>
  );
});

export default BoletaCard;

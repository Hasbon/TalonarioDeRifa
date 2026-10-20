import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { publicApi } from '../services/api';
import { formatCOP, formatDate, formatDateTime } from '../utils/format';
import './PublicBoleta.css';

export default function PublicBoleta() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setData(await publicApi.getBoleta(token));
      } catch (e) {
        setError(e.response?.data?.detail || 'Boleta no encontrada');
      }
    })();
  }, [token]);

  if (error) {
    return (
      <main className="boleta-validate container">
        <div className="alert alert-error">{error}</div>
        <Link to="/">Ir a la rifa</Link>
      </main>
    );
  }
  if (!data) {
    return (
      <main className="boleta-validate container">
        <p className="alert alert-info">Validando boleta…</p>
      </main>
    );
  }

  const validityLabel =
    data.validity === 'valid'
      ? 'Válida'
      : data.validity === 'revoked'
        ? 'Anulada'
        : 'Estado desconocido';

  return (
    <main className="boleta-validate container">
      <div className={`validate-card validate-card--${data.validity}`}>
        <p className="validate-card__eyebrow">Validación pública</p>
        <h1>{data.raffle_name}</h1>
        <div className="validate-card__number">{data.number_code}</div>
        <p className="validate-card__status">{validityLabel}</p>
        <ul>
          <li>
            <strong>Asignación:</strong>{' '}
            {data.assignment_status === 'active'
              ? 'Activa'
              : data.assignment_status === 'cancelled'
                ? 'Anulada'
                : 'Sin asignación'}
          </li>
          <li>
            <strong>Sorteo:</strong> {formatDate(data.draw_date)}
          </li>
          <li>
            <strong>Entrega:</strong> {formatDateTime(data.delivery_datetime)}
          </li>
          <li>
            <strong>Premio:</strong> {data.primary_prize}
          </li>
          <li>
            <strong>Alternativa:</strong> {formatCOP(data.alternative_prize_amount)}
          </li>
          <li>
            <strong>Precio de boleta:</strong> {formatCOP(data.ticket_price)}
          </li>
          {data.financial_label && (
            <li>
              <strong>Estado financiero (informativo):</strong> {data.financial_label}
            </li>
          )}
        </ul>
        <p className="validate-card__note">
          Esta página no muestra teléfonos, abonos exactos, deudas ni datos del vendedor. La imagen
          descargada de una boleta no sustituye esta validación en línea.
        </p>
        <Link className="btn btn-primary" to="/">
          Ver tablero público
        </Link>
      </div>
    </main>
  );
}

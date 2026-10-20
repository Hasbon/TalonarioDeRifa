import { Link } from 'react-router-dom';
import { formatCOP, formatDate } from '../utils/format';
import './PublicHeader.css';

export default function PublicHeader({ raffle, compact = false }) {
  if (!raffle) return null;

  return (
    <header className={`public-header${compact ? ' public-header--compact' : ''}`}>
      {!compact && (
        <>
          <p className="public-header__eyebrow">Talonario digital</p>
          <h1 className="public-header__title">{raffle.name}</h1>
          <p className="public-header__desc">{raffle.description}</p>
        </>
      )}
      <div className="public-header__meta">
        <div>
          <span className="label">Sorteo</span>
          <strong>{formatDate(raffle.draw_date)}</strong>
        </div>
        <div>
          <span className="label">Boleta</span>
          <strong className="price">{formatCOP(raffle.ticket_price)}</strong>
        </div>
      </div>
      <Link to="/login" className="btn btn-ghost public-header__login">
        Acceso vendedores
      </Link>
    </header>
  );
}

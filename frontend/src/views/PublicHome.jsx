import NumberBoard from '../components/NumberBoard';
import PublicHeader from '../components/PublicHeader';
import { FLYER_ALT, granRifaFlyerUrl } from '../assets/raffleAssets';
import { usePublicTickets } from '../hooks/usePublicTickets';
import { formatCOP, formatDateTime } from '../utils/format';
import './PublicHome.css';

export default function PublicHome() {
  const { tickets, raffle, error, loading } = usePublicTickets();

  if (loading) {
    return (
      <main className="container public-home">
        <p className="alert alert-info">Cargando rifa…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="container public-home">
        <p className="alert alert-error">{error}</p>
      </main>
    );
  }

  const available = tickets.filter((t) => t.available).length;

  return (
    <main className="public-home">
      <section className="hero-flyer" aria-label="Gran Rifa de Fin de Año">
        <img
          className="hero-flyer__image"
          src={granRifaFlyerUrl}
          alt={FLYER_ALT}
          width={1200}
          height={1600}
          decoding="async"
          fetchPriority="high"
        />
        <div className="hero-flyer__overlay">
          <PublicHeader raffle={raffle} compact />
        </div>
      </section>

      <div className="container public-home__body">
        <section className="prize-section" aria-labelledby="premio-title">
          <h2 id="premio-title">Premio y condiciones</h2>
          <img
            className="prize-flyer"
            src={granRifaFlyerUrl}
            alt={FLYER_ALT}
            width={800}
            height={1067}
            loading="lazy"
            decoding="async"
          />
          <p className="prize-main">{raffle.primary_prize}</p>
          <p className="prize-alt">
            Alternativa en efectivo:{' '}
            <strong>{formatCOP(raffle.alternative_prize_amount)}</strong>, sujeta a las
            condiciones oficiales de la rifa.
          </p>
          <p className="prize-note">
            Entrega: {formatDateTime(raffle.delivery_datetime)} (hora Colombia).
          </p>
        </section>

        <section className="board-section" aria-labelledby="tablero-title">
          <h2 id="tablero-title">Tablero de números</h2>
          <p>
            {available} disponibles · {100 - available} no disponibles. El tablero se actualiza
            automáticamente.
          </p>
          <div className="board-legend">
            <span>
              <i className="swatch green" /> Disponible
            </span>
            <span>
              <i className="swatch red" /> No disponible
            </span>
          </div>
          <NumberBoard tickets={tickets} />
        </section>

        <section className="info-section" aria-labelledby="sorteo-title">
          <h2 id="sorteo-title">Información del sorteo</h2>
          <ul className="info-list">
            <li>
              <strong>Lotería:</strong> {raffle.lottery_name}
            </li>
            <li>
              <strong>Referencia:</strong> {raffle.lottery_draw_reference}
            </li>
            <li>
              <strong>Cómo se elige el ganador:</strong> las dos últimas cifras del premio mayor
              del sorteo definido. Este sitio no publica resultados no verificados.
            </li>
          </ul>
        </section>

        <section className="rules-section" aria-labelledby="reglamento-title">
          <h2 id="reglamento-title">Reglamento</h2>
          <pre className="rules-text">{raffle.public_rules}</pre>
        </section>

        <section className="contact-section">
          <h2>Contacto</h2>
          <p>{raffle.public_contact}</p>
          <h3>Aviso de privacidad</h3>
          <p className="privacy">{raffle.privacy_notice}</p>
        </section>

        <footer className="public-footer">
          <p>
            Antes de comercializar, verifique los requisitos legales aplicables en Colombia. Este
            software no constituye autorización oficial.
          </p>
        </footer>
      </div>
    </main>
  );
}

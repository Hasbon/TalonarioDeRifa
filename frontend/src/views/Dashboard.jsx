import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import NumberBoard from '../components/NumberBoard';
import { adminApi, publicApi, salesApi } from '../services/api';
import { formatCOP } from '../utils/format';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [salesByNumber, setSalesByNumber] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [s, t, sales] = await Promise.all([
          adminApi.reports(),
          publicApi.getTickets(),
          salesApi.list({ commercial_status: 'active' }),
        ]);
        setStats(s);
        setTickets(t);
        const map = {};
        sales.forEach((sale) => {
          map[sale.number_code] = sale;
        });
        setSalesByNumber(map);
      } catch (e) {
        setError(e.response?.data?.detail || 'Error al cargar tablero');
      }
    })();
  }, []);

  const onSelect = (ticket) => {
    const sale = salesByNumber[ticket.number_code];
    if (sale) {
      window.location.href = `/app/ventas/${sale.id}`;
    } else {
      window.location.href = `/app/nueva-venta?numero=${ticket.number_code}`;
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard__head">
        <h1>Panel de ventas</h1>
        <Link className="btn btn-primary" to="/app/nueva-venta">
          Nueva venta
        </Link>
      </header>
      {error && <div className="alert alert-error">{error}</div>}
      {stats && (
        <div className="kpi-grid">
          <div className="kpi">
            <span>Disponibles</span>
            <strong>{stats.available}</strong>
          </div>
          <div className="kpi">
            <span>Asignados</span>
            <strong>{stats.assigned}</strong>
          </div>
          <div className="kpi">
            <span>Recibido</span>
            <strong>{formatCOP(stats.total_received)}</strong>
          </div>
          <div className="kpi">
            <span>Pendiente</span>
            <strong>{formatCOP(stats.total_outstanding)}</strong>
          </div>
          <div className="kpi">
            <span>Clientes</span>
            <strong>{stats.customers_count}</strong>
          </div>
          <div className="kpi warn">
            <span>Compromisos vencidos</span>
            <strong>{stats.overdue_commitments}</strong>
          </div>
        </div>
      )}
      <p className="dashboard__hint">
        Toque un número disponible para venderlo, o uno asignado para ver su ficha.
      </p>
      <NumberBoard tickets={tickets} interactive onSelect={onSelect} />
    </div>
  );
}

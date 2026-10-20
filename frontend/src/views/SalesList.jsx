import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { salesApi } from '../services/api';
import { formatCOP, paymentStatusLabel } from '../utils/format';
import './FormPages.css';

export default function SalesList() {
  const [sales, setSales] = useState([]);
  const [filters, setFilters] = useState({
    number_code: '',
    customer_name: '',
    phone: '',
    payment_status: '',
    commercial_status: 'active',
  });
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '' && v != null)
      );
      setSales(await salesApi.list(params));
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al cargar ventas');
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="form-page">
      <h1>Ventas</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="filters">
        <input
          placeholder="Número"
          value={filters.number_code}
          onChange={(e) => setFilters({ ...filters, number_code: e.target.value })}
        />
        <input
          placeholder="Nombre"
          value={filters.customer_name}
          onChange={(e) => setFilters({ ...filters, customer_name: e.target.value })}
        />
        <input
          placeholder="Teléfono"
          value={filters.phone}
          onChange={(e) => setFilters({ ...filters, phone: e.target.value })}
        />
        <select
          value={filters.payment_status}
          onChange={(e) => setFilters({ ...filters, payment_status: e.target.value })}
        >
          <option value="">Estado pago</option>
          <option value="unpaid">Sin pagos</option>
          <option value="partial">Parcial</option>
          <option value="paid">Pagada</option>
        </select>
        <select
          value={filters.commercial_status}
          onChange={(e) => setFilters({ ...filters, commercial_status: e.target.value })}
        >
          <option value="">Todas</option>
          <option value="active">Activas</option>
          <option value="cancelled">Anuladas</option>
        </select>
        <button type="button" className="btn btn-primary" onClick={load}>
          Filtrar
        </button>
      </div>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Nº</th>
              <th>Cliente</th>
              <th>Teléfono</th>
              <th>Pagado</th>
              <th>Saldo</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {sales.map((s) => (
              <tr key={s.id}>
                <td>
                  <strong>{s.number_code}</strong>
                </td>
                <td>{s.customer.full_name}</td>
                <td>{s.customer.phone}</td>
                <td>{formatCOP(s.total_paid)}</td>
                <td>{formatCOP(s.balance_due)}</td>
                <td>
                  <span className={`badge badge-${s.payment_status}`}>
                    {s.commercial_status === 'cancelled'
                      ? 'Anulada'
                      : paymentStatusLabel(s.payment_status)}
                  </span>
                </td>
                <td>
                  <Link to={`/app/ventas/${s.id}`}>Ver</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

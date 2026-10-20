import { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { adminApi } from '../services/api';
import { formatCOP } from '../utils/format';
import './FormPages.css';

export default function Reports() {
  const { isAdmin, user } = useAuth();
  const [stats, setStats] = useState(null);
  const [bySeller, setBySeller] = useState([]);
  const [overdue, setOverdue] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [s, o] = await Promise.all([adminApi.reports(), adminApi.overdue()]);
        setStats(s);
        setOverdue(o);
        if (user?.role === 'admin') {
          setBySeller(await adminApi.reportsBySeller());
        }
      } catch (e) {
        setError(e.response?.data?.detail || 'Error al cargar reportes');
      }
    })();
  }, [user]);

  const downloadCsv = async () => {
    const token = localStorage.getItem('access_token');
    const res = await fetch(adminApi.exportCsvUrl(), {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'reporte_ventas.csv';
    a.click();
  };

  return (
    <div className="form-page">
      <h1>Reportes</h1>
      {error && <div className="alert alert-error">{error}</div>}
      {stats && (
        <div className="kpi-grid" style={{ marginBottom: '1.25rem' }}>
          <div className="kpi">
            <span>Disponibles</span>
            <strong>{stats.available}</strong>
          </div>
          <div className="kpi">
            <span>Asignados</span>
            <strong>{stats.assigned}</strong>
          </div>
          <div className="kpi">
            <span>Recaudado real</span>
            <strong>{formatCOP(stats.total_received)}</strong>
          </div>
          <div className="kpi">
            <span>Saldos pendientes</span>
            <strong>{formatCOP(stats.total_outstanding)}</strong>
          </div>
          <div className="kpi">
            <span>Abonos parciales (suma)</span>
            <strong>{formatCOP(stats.total_partial_payments_sum)}</strong>
          </div>
          <div className="kpi warn">
            <span>Compromisos vencidos</span>
            <strong>{stats.overdue_commitments}</strong>
          </div>
        </div>
      )}
      <p className="alert alert-info">
        El valor de boletas asignadas no es lo mismo que el dinero recaudado. Solo cuentan los pagos
        confirmados.
      </p>
      {isAdmin && (
        <button type="button" className="btn btn-primary" onClick={downloadCsv}>
          Exportar CSV
        </button>
      )}

      {isAdmin && bySeller.length > 0 && (
        <>
          <h2>Ventas por vendedor</h2>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Vendedor</th>
                  <th>Ventas</th>
                  <th>Recibido</th>
                  <th>Pendiente</th>
                </tr>
              </thead>
              <tbody>
                {bySeller.map((r) => (
                  <tr key={r.seller_id}>
                    <td>{r.seller_name}</td>
                    <td>{r.sales_count}</td>
                    <td>{formatCOP(r.received)}</td>
                    <td>{formatCOP(r.outstanding)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <h2>Compromisos vencidos</h2>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Nº</th>
              <th>Cliente</th>
              <th>Teléfono</th>
              <th>Saldo</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {overdue.map((o) => (
              <tr key={o.sale_id}>
                <td>{o.number_code}</td>
                <td>{o.customer}</td>
                <td>{o.phone}</td>
                <td>{formatCOP(o.balance)}</td>
                <td>{o.payment_due_date}</td>
              </tr>
            ))}
            {overdue.length === 0 && (
              <tr>
                <td colSpan={5}>Sin compromisos vencidos</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

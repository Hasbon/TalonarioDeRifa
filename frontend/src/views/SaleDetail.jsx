import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { salesApi } from '../services/api';
import { formatCOP, formatDate, formatDateTime, paymentStatusLabel } from '../utils/format';
import './FormPages.css';

export default function SaleDetail() {
  const { saleId } = useParams();
  const { isAdmin } = useAuth();
  const [sale, setSale] = useState(null);
  const [error, setError] = useState('');
  const [payment, setPayment] = useState({ amount: '', payment_method: 'efectivo', payment_reference: '' });
  const [cancelReason, setCancelReason] = useState('');
  const [msg, setMsg] = useState('');

  const load = async () => {
    try {
      setSale(await salesApi.get(saleId));
    } catch (e) {
      setError(e.response?.data?.detail || 'No se encontró la venta');
    }
  };

  useEffect(() => {
    load();
  }, [saleId]);

  const addPayment = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await salesApi.addPayment(saleId, {
        amount: Number(payment.amount),
        payment_method: payment.payment_method,
        payment_reference: payment.payment_reference || null,
        confirm: true,
      });
      setPayment({ amount: '', payment_method: 'efectivo', payment_reference: '' });
      setMsg('Abono registrado');
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar pago');
    }
  };

  const cancel = async () => {
    if (!cancelReason.trim() || cancelReason.trim().length < 5) {
      setError('Indique un motivo de anulación (mín. 5 caracteres)');
      return;
    }
    try {
      await salesApi.cancel(saleId, cancelReason.trim());
      setMsg('Asignación anulada. El historial se conservó.');
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo anular');
    }
  };

  if (!sale && !error) return <p className="alert alert-info">Cargando…</p>;
  if (error && !sale) return <div className="alert alert-error">{error}</div>;

  return (
    <div className="form-page">
      <h1>
        Boleta {sale.number_code}{' '}
        <span className={`badge badge-${sale.payment_status}`}>
          {sale.commercial_status === 'cancelled'
            ? 'Anulada'
            : paymentStatusLabel(sale.payment_status)}
        </span>
      </h1>
      {msg && <div className="alert alert-success">{msg}</div>}
      {error && <div className="alert alert-error">{String(error)}</div>}

      <div className="form-card">
        <p>
          <strong>Comprador:</strong> {sale.customer.full_name}
        </p>
        <p>
          <strong>Teléfono:</strong> {sale.customer.phone}
        </p>
        <p>
          <strong>Precio:</strong> {formatCOP(sale.ticket_price)} · <strong>Pagado:</strong>{' '}
          {formatCOP(sale.total_paid)} · <strong>Saldo:</strong> {formatCOP(sale.balance_due)}
        </p>
        <p>
          <strong>Asignada:</strong> {formatDateTime(sale.assigned_at)}
        </p>
        <p>
          <strong>Compromiso de pago:</strong> {formatDate(sale.payment_due_date)}
        </p>
        <p>
          <strong>Vendedor:</strong> {sale.seller.full_name}
        </p>
        {sale.internal_notes && (
          <p>
            <strong>Observaciones:</strong> {sale.internal_notes}
          </p>
        )}
        {sale.cancellation_reason && (
          <p>
            <strong>Motivo anulación:</strong> {sale.cancellation_reason}
          </p>
        )}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Link className="btn btn-gold" to={`/app/boleta/${sale.id}`}>
            Generar boleta digital
          </Link>
        </div>
      </div>

      <h2>Historial de pagos</h2>
      <div className="table-wrap" style={{ marginBottom: '1.25rem' }}>
        <table className="data">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Monto</th>
              <th>Método</th>
              <th>Estado</th>
              <th>Ref.</th>
            </tr>
          </thead>
          <tbody>
            {sale.payments.map((p) => (
              <tr key={p.id}>
                <td>{formatDateTime(p.payment_date)}</td>
                <td>{formatCOP(p.amount)}</td>
                <td>{p.payment_method}</td>
                <td>{p.status}</td>
                <td>{p.payment_reference || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sale.commercial_status === 'active' && sale.balance_due > 0 && (
        <form className="form-card" onSubmit={addPayment} style={{ marginBottom: '1.25rem' }}>
          <h3>Registrar abono</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Monto</label>
              <input
                type="number"
                min={1}
                max={sale.balance_due}
                value={payment.amount}
                onChange={(e) => setPayment({ ...payment, amount: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Método</label>
              <select
                value={payment.payment_method}
                onChange={(e) => setPayment({ ...payment, payment_method: e.target.value })}
              >
                <option value="efectivo">Efectivo</option>
                <option value="transferencia">Transferencia</option>
                <option value="nequi">Nequi</option>
                <option value="daviplata">Daviplata</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Referencia</label>
            <input
              value={payment.payment_reference}
              onChange={(e) => setPayment({ ...payment, payment_reference: e.target.value })}
            />
          </div>
          <button className="btn btn-primary" type="submit">
            Registrar pago
          </button>
        </form>
      )}

      {isAdmin && sale.commercial_status === 'active' && (
        <div className="form-card">
          <h3>Anular asignación</h3>
          <p>Libera el número sin borrar el historial financiero.</p>
          <div className="form-group">
            <label>Motivo obligatorio</label>
            <textarea
              rows={3}
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
            />
          </div>
          <button type="button" className="btn btn-danger" onClick={cancel}>
            Anular asignación
          </button>
        </div>
      )}
    </div>
  );
}

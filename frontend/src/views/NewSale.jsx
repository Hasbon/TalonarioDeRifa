import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { publicApi, salesApi } from '../services/api';
import { formatCOP } from '../utils/format';
import './FormPages.css';

export default function NewSale() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [ticketPrice, setTicketPrice] = useState(35000);
  const [form, setForm] = useState({
    customer_full_name: '',
    customer_phone: '',
    number_code: params.get('numero') || '',
    initial_payment: 0,
    payment_method: 'efectivo',
    payment_reference: '',
    payment_due_date: '',
    internal_notes: '',
  });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    publicApi.getRaffle().then((r) => setTicketPrice(r.ticket_price)).catch(() => {});
  }, []);

  const balance = useMemo(() => {
    const abono = Number(form.initial_payment) || 0;
    return Math.max(0, ticketPrice - abono);
  }, [form.initial_payment, ticketPrice]);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const body = {
        ...form,
        number_code: form.number_code.padStart(2, '0'),
        initial_payment: Number(form.initial_payment) || 0,
        payment_due_date: form.payment_due_date || null,
        payment_reference: form.payment_reference || null,
        internal_notes: form.internal_notes || null,
      };
      const sale = await salesApi.create(body);
      navigate(`/app/boleta/${sale.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo registrar la venta');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Registrar venta</h1>
      <p>
        Precio de boleta: <strong>{formatCOP(ticketPrice)}</strong>. El número queda ocupado
        aunque el abono sea cero.
      </p>
      {error && <div className="alert alert-error">{String(error)}</div>}
      <form onSubmit={onSubmit} className="form-card">
        <div className="form-group">
          <label htmlFor="name">Nombre completo</label>
          <input id="name" value={form.customer_full_name} onChange={set('customer_full_name')} required />
        </div>
        <div className="form-group">
          <label htmlFor="phone">Teléfono</label>
          <input id="phone" value={form.customer_phone} onChange={set('customer_phone')} required />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="number">Número (00-99)</label>
            <input
              id="number"
              value={form.number_code}
              onChange={set('number_code')}
              pattern="\d{1,2}"
              maxLength={2}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="abono">Abono inicial</label>
            <input
              id="abono"
              type="number"
              min={0}
              max={ticketPrice}
              value={form.initial_payment}
              onChange={set('initial_payment')}
            />
          </div>
        </div>
        <p className="balance-line">
          Saldo pendiente calculado: <strong>{formatCOP(balance)}</strong>
        </p>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="method">Método de pago</label>
            <select id="method" value={form.payment_method} onChange={set('payment_method')}>
              <option value="efectivo">Efectivo</option>
              <option value="transferencia">Transferencia</option>
              <option value="nequi">Nequi</option>
              <option value="daviplata">Daviplata</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="due">Fecha compromiso de pago</label>
            <input id="due" type="date" value={form.payment_due_date} onChange={set('payment_due_date')} />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="ref">Referencia / comprobante (opcional)</label>
          <input id="ref" value={form.payment_reference} onChange={set('payment_reference')} />
        </div>
        <div className="form-group">
          <label htmlFor="notes">Observaciones internas</label>
          <textarea id="notes" rows={3} value={form.internal_notes} onChange={set('internal_notes')} />
        </div>
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? 'Guardando…' : 'Asignar número'}
        </button>
      </form>
    </div>
  );
}

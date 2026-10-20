import { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import './FormPages.css';

export default function RaffleConfig() {
  const [form, setForm] = useState(null);
  const [priceReason, setPriceReason] = useState('');
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [originalPrice, setOriginalPrice] = useState(null);

  useEffect(() => {
    adminApi
      .getRaffle()
      .then((r) => {
        setForm({
          ...r,
          delivery_datetime: r.delivery_datetime?.slice(0, 16) || '',
        });
        setOriginalPrice(r.ticket_price);
      })
      .catch((e) => setError(e.response?.data?.detail || 'Error'));
  }, []);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const save = async (e) => {
    e.preventDefault();
    setError('');
    setMsg('');
    try {
      const body = {
        name: form.name,
        description: form.description,
        primary_prize: form.primary_prize,
        alternative_prize_amount: Number(form.alternative_prize_amount),
        ticket_price: Number(form.ticket_price),
        draw_date: form.draw_date,
        delivery_datetime: new Date(form.delivery_datetime).toISOString(),
        lottery_name: form.lottery_name,
        lottery_draw_reference: form.lottery_draw_reference,
        public_contact: form.public_contact,
        public_rules: form.public_rules,
        privacy_notice: form.privacy_notice,
        logo_url: form.logo_url || null,
      };
      if (Number(form.ticket_price) !== originalPrice) {
        body.price_change_reason = priceReason;
      }
      const updated = await adminApi.updateRaffle(body);
      setOriginalPrice(updated.ticket_price);
      setMsg('Configuración guardada. El precio nuevo no altera ventas existentes.');
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo guardar');
    }
  };

  if (!form) return <p className="alert alert-info">Cargando…</p>;

  return (
    <div className="form-page">
      <h1>Configuración de la rifa</h1>
      {msg && <div className="alert alert-success">{msg}</div>}
      {error && <div className="alert alert-error">{String(error)}</div>}
      <form className="form-card" onSubmit={save}>
        <div className="form-group">
          <label>Nombre</label>
          <input value={form.name} onChange={set('name')} required />
        </div>
        <div className="form-group">
          <label>Descripción</label>
          <textarea rows={2} value={form.description} onChange={set('description')} />
        </div>
        <div className="form-group">
          <label>Premio principal</label>
          <textarea rows={2} value={form.primary_prize} onChange={set('primary_prize')} />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Premio alternativo (COP)</label>
            <input
              type="number"
              value={form.alternative_prize_amount}
              onChange={set('alternative_prize_amount')}
            />
          </div>
          <div className="form-group">
            <label>Precio boleta (COP)</label>
            <input type="number" value={form.ticket_price} onChange={set('ticket_price')} />
          </div>
        </div>
        {Number(form.ticket_price) !== originalPrice && (
          <div className="form-group">
            <label>Motivo del cambio de precio (obligatorio)</label>
            <input value={priceReason} onChange={(e) => setPriceReason(e.target.value)} required />
          </div>
        )}
        <div className="form-row">
          <div className="form-group">
            <label>Fecha sorteo</label>
            <input type="date" value={form.draw_date} onChange={set('draw_date')} />
          </div>
          <div className="form-group">
            <label>Entrega</label>
            <input
              type="datetime-local"
              value={form.delivery_datetime}
              onChange={set('delivery_datetime')}
            />
          </div>
        </div>
        <div className="form-group">
          <label>Lotería</label>
          <input value={form.lottery_name} onChange={set('lottery_name')} />
        </div>
        <div className="form-group">
          <label>Referencia del sorteo</label>
          <input value={form.lottery_draw_reference} onChange={set('lottery_draw_reference')} />
        </div>
        <div className="form-group">
          <label>Contacto público</label>
          <textarea rows={2} value={form.public_contact} onChange={set('public_contact')} />
        </div>
        <div className="form-group">
          <label>Reglamento</label>
          <textarea rows={6} value={form.public_rules} onChange={set('public_rules')} />
        </div>
        <div className="form-group">
          <label>Aviso de privacidad</label>
          <textarea rows={4} value={form.privacy_notice} onChange={set('privacy_notice')} />
        </div>
        <div className="form-group">
          <label>URL del logo (opcional)</label>
          <input value={form.logo_url || ''} onChange={set('logo_url')} />
        </div>
        <button className="btn btn-primary" type="submit">
          Guardar
        </button>
      </form>
    </div>
  );
}

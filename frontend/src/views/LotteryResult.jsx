import { useEffect, useState } from 'react';
import { resultsApi } from '../services/api';
import './FormPages.css';

export default function LotteryResult() {
  const [results, setResults] = useState([]);
  const [form, setForm] = useState({
    lottery_name: 'Lotería del Valle',
    draw_reference: '',
    draw_date: '2026-12-30',
    winning_number: '',
    official_source_url: '',
    notes: '',
  });
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');

  const load = async () => setResults(await resultsApi.list());

  useEffect(() => {
    load().catch((e) => setError(e.response?.data?.detail || 'Error'));
  }, []);

  const create = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const created = await resultsApi.create(form);
      setMsg(
        `Resultado registrado. Número ganador derivado: ${created.derived_winner_code}. Aún no es oficial hasta confirmar.`
      );
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo registrar');
    }
  };

  const confirm = async (id) => {
    try {
      const r = await resultsApi.confirm(id);
      setMsg(
        r.has_active_assignment
          ? `Confirmado. Ganador del número ${r.derived_winner_code}: ${r.winner_customer_name}`
          : `Confirmado. El número ${r.derived_winner_code} no tiene asignación activa. No se inventa un suplente.`
      );
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo confirmar');
    }
  };

  return (
    <div className="form-page">
      <h1>Resultado del sorteo</h1>
      <p className="alert alert-info">
        No declare un resultado oficial hasta verificar la fuente. El sistema deriva las dos últimas
        cifras del premio mayor; no hay sorteo aleatorio.
      </p>
      {msg && <div className="alert alert-success">{msg}</div>}
      {error && <div className="alert alert-error">{String(error)}</div>}

      <form className="form-card" onSubmit={create} style={{ marginBottom: '1.25rem' }}>
        <h2>Registrar resultado verificado</h2>
        <div className="form-group">
          <label>Lotería</label>
          <input
            value={form.lottery_name}
            onChange={(e) => setForm({ ...form, lottery_name: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>Referencia oficial</label>
          <input
            value={form.draw_reference}
            onChange={(e) => setForm({ ...form, draw_reference: e.target.value })}
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Fecha del sorteo</label>
            <input
              type="date"
              value={form.draw_date}
              onChange={(e) => setForm({ ...form, draw_date: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Número completo del premio mayor</label>
            <input
              value={form.winning_number}
              onChange={(e) => setForm({ ...form, winning_number: e.target.value })}
              placeholder="Ej. 458147"
              required
            />
          </div>
        </div>
        <div className="form-group">
          <label>URL de la fuente oficial</label>
          <input
            value={form.official_source_url}
            onChange={(e) => setForm({ ...form, official_source_url: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>Notas</label>
          <textarea
            rows={2}
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </div>
        <button className="btn btn-primary" type="submit">
          Registrar borrador
        </button>
      </form>

      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Premio mayor</th>
              <th>Ganador (2 cifras)</th>
              <th>Estado</th>
              <th>Asignación</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.id}>
                <td>{r.winning_number}</td>
                <td>
                  <strong>{r.derived_winner_code}</strong>
                </td>
                <td>{r.verification_status}</td>
                <td>
                  {r.has_active_assignment === false
                    ? 'Sin asignación activa'
                    : r.has_active_assignment
                      ? 'Con asignación'
                      : '—'}
                </td>
                <td>
                  {r.verification_status !== 'confirmed' && (
                    <button type="button" className="btn btn-gold" onClick={() => confirm(r.id)}>
                      Confirmar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

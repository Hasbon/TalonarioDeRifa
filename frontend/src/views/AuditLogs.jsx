import { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { formatDateTime } from '../utils/format';
import './FormPages.css';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    adminApi
      .auditLogs()
      .then(setLogs)
      .catch((e) => setError(e.response?.data?.detail || 'Error'));
  }, []);

  return (
    <div className="form-page">
      <h1>Auditoría</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Acción</th>
              <th>Entidad</th>
              <th>Motivo</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id}>
                <td>{formatDateTime(l.created_at)}</td>
                <td>{l.action}</td>
                <td>
                  {l.entity_type} {l.entity_id ? `#${l.entity_id.slice(0, 8)}` : ''}
                </td>
                <td>{l.reason || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

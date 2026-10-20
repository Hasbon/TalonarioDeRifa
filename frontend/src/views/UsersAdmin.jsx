import { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import './FormPages.css';

export default function UsersAdmin() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    username: '',
    password: '',
    full_name: '',
    role: 'seller',
  });
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');

  const load = async () => setUsers(await adminApi.listUsers());

  useEffect(() => {
    load().catch((e) => setError(e.response?.data?.detail || 'Error'));
  }, []);

  const create = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await adminApi.createUser(form);
      setMsg('Usuario creado');
      setForm({ username: '', password: '', full_name: '', role: 'seller' });
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo crear');
    }
  };

  const toggleActive = async (u) => {
    await adminApi.updateUser(u.id, { is_active: !u.is_active });
    await load();
  };

  return (
    <div className="form-page">
      <h1>Usuarios</h1>
      {error && <div className="alert alert-error">{String(error)}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}
      <form className="form-card" onSubmit={create} style={{ marginBottom: '1.25rem' }}>
        <h2>Crear vendedor / admin</h2>
        <div className="form-row">
          <div className="form-group">
            <label>Usuario</label>
            <input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Nombre</label>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Contraseña (mín. 10)</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              minLength={10}
              required
            />
          </div>
          <div className="form-group">
            <label>Rol</label>
            <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="seller">Vendedor</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
        </div>
        <button className="btn btn-primary" type="submit">
          Crear usuario
        </button>
      </form>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Activo</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.full_name}</td>
                <td>{u.role}</td>
                <td>{u.is_active ? 'Sí' : 'No'}</td>
                <td>
                  <button type="button" className="btn btn-ghost" onClick={() => toggleActive(u)}>
                    {u.is_active ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

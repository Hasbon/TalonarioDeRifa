import { Outlet, Navigate } from 'react-router-dom';
import AppMenu from '../components/AppMenu';
import { useAuth } from '../hooks/useAuth';
import './AppLayout.css';

export default function AppLayout() {
  const { user, loading, logout, isAdmin } = useAuth();

  if (loading) {
    return <p className="container alert alert-info">Cargando sesión…</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-shell">
      <AppMenu user={user} isAdmin={isAdmin} onLogout={logout} />
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}

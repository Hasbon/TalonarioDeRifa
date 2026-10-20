import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function AdminOnly({ children }) {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return <p className="alert alert-info">Cargando…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/app" replace />;
  return children;
}

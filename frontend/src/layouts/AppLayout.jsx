import { useEffect, useState } from 'react';
import { NavLink, Outlet, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './AppLayout.css';

export default function AppLayout() {
  const { user, loading, logout, isAdmin } = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  if (loading) {
    return <p className="container alert alert-info">Cargando sesión…</p>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className={`app-shell${menuOpen ? ' app-shell--menu-open' : ''}`}>
      <aside className="app-nav">
        <div className="app-nav__top">
          <div className="app-nav__brand">
            <strong>Rifa Digital</strong>
            <span>{user.full_name}</span>
            <small>{isAdmin ? 'Administrador' : 'Vendedor'}</small>
          </div>
          <button
            type="button"
            className="app-nav__toggle"
            aria-expanded={menuOpen}
            aria-controls="app-nav-panel"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span className="app-nav__toggle-bars" aria-hidden="true" />
            {menuOpen ? 'Ocultar menú' : 'Menú'}
          </button>
        </div>

        <div id="app-nav-panel" className="app-nav__panel">
          <nav>
            <NavLink to="/app" end>
              Tablero
            </NavLink>
            <NavLink to="/app/nueva-venta">Nueva venta</NavLink>
            <NavLink to="/app/ventas">Mis ventas</NavLink>
            <NavLink to="/app/reportes">Reportes</NavLink>
            {isAdmin && (
              <>
                <NavLink to="/app/usuarios">Usuarios</NavLink>
                <NavLink to="/app/configuracion">Configuración</NavLink>
                <NavLink to="/app/resultado">Resultado</NavLink>
                <NavLink to="/app/auditoria">Auditoría</NavLink>
              </>
            )}
          </nav>
          <button type="button" className="btn btn-ghost" onClick={logout}>
            Cerrar sesión
          </button>
          <a className="app-nav__public" href="/">
            Ver página pública
          </a>
        </div>
      </aside>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}

import { useLocation, useNavigate } from 'react-router-dom';
import './AppMenu.css';

const SELLER_ITEMS = [
  { path: '/app', label: 'Tablero', match: 'exact' },
  { path: '/app/nueva-venta', label: 'Nueva venta', match: 'exact' },
  { path: '/app/ventas', label: 'Mis ventas', match: 'prefix' },
  { path: '/app/reportes', label: 'Reportes', match: 'exact' },
];

const ADMIN_ITEMS = [
  { path: '/app/usuarios', label: 'Usuarios', match: 'exact' },
  { path: '/app/configuracion', label: 'Configuración', match: 'exact' },
  { path: '/app/resultado', label: 'Resultado', match: 'exact' },
  { path: '/app/auditoria', label: 'Auditoría', match: 'exact' },
];

function pathMatchesItem(pathname, item) {
  if (item.match === 'prefix') {
    return pathname === item.path || pathname.startsWith(`${item.path}/`);
  }
  if (item.path === '/app') {
    return pathname === '/app' || pathname === '/app/';
  }
  return pathname === item.path;
}

function isBoletaPath(pathname) {
  return pathname.startsWith('/app/boleta/');
}

export default function AppMenu({ user, isAdmin, onLogout }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const items = isAdmin ? [...SELLER_ITEMS, ...ADMIN_ITEMS] : SELLER_ITEMS;

  return (
    <header className="app-menu">
      <div className="app-menu__brand">
        <strong>Rifa Digital</strong>
        <span className="app-menu__user">{user.full_name}</span>
        <small className="app-menu__role">{isAdmin ? 'Administrador' : 'Vendedor'}</small>
      </div>

      <div className="app-menu__radio" role="group" aria-label="Navegación del panel">
        {items.map((item) => {
          const id = `app-nav-${item.path.replace(/\//g, '-') || 'app'}`;
          const checked =
            pathMatchesItem(pathname, item) ||
            (item.path === '/app/ventas' && isBoletaPath(pathname));
          return (
            <label key={item.path} htmlFor={id}>
              <input
                type="radio"
                id={id}
                name="app-main-nav"
                checked={checked}
                onChange={() => navigate(item.path)}
              />
              {item.label}
            </label>
          );
        })}
      </div>

      <div className="app-menu__actions">
        <a className="app-menu__public" href="/">
          Página pública
        </a>
        <button type="button" className="app-menu__logout" onClick={onLogout}>
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}

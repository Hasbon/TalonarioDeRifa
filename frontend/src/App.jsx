import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AdminOnly from './components/AdminOnly';
import AppLayout from './layouts/AppLayout';
import AuditLogs from './views/AuditLogs';
import BoletaView from './views/BoletaView';
import Dashboard from './views/Dashboard';
import Login from './views/Login';
import LotteryResult from './views/LotteryResult';
import NewSale from './views/NewSale';
import PublicBoleta from './views/PublicBoleta';
import PublicHome from './views/PublicHome';
import RaffleConfig from './views/RaffleConfig';
import Reports from './views/Reports';
import SaleDetail from './views/SaleDetail';
import SalesList from './views/SalesList';
import UsersAdmin from './views/UsersAdmin';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PublicHome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/boleta/:token" element={<PublicBoleta />} />
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="nueva-venta" element={<NewSale />} />
          <Route path="ventas" element={<SalesList />} />
          <Route path="ventas/:saleId" element={<SaleDetail />} />
          <Route path="boleta/:saleId" element={<BoletaView />} />
          <Route path="reportes" element={<Reports />} />
          <Route
            path="usuarios"
            element={
              <AdminOnly>
                <UsersAdmin />
              </AdminOnly>
            }
          />
          <Route
            path="configuracion"
            element={
              <AdminOnly>
                <RaffleConfig />
              </AdminOnly>
            }
          />
          <Route
            path="resultado"
            element={
              <AdminOnly>
                <LotteryResult />
              </AdminOnly>
            }
          />
          <Route
            path="auditoria"
            element={
              <AdminOnly>
                <AuditLogs />
              </AdminOnly>
            }
          />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

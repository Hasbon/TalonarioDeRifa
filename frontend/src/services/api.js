import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/boleta')) {
        const isPublic =
          window.location.pathname === '/' ||
          window.location.pathname.startsWith('/boleta');
        if (!isPublic && window.location.pathname.startsWith('/app')) {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const publicApi = {
  getRaffle: () => api.get('/public/raffle').then((r) => r.data),
  getTickets: () => api.get('/public/tickets').then((r) => r.data),
  getTicket: (code) => api.get(`/public/tickets/${code}`).then((r) => r.data),
  getBoleta: (token) => api.get(`/public/boletas/${token}`).then((r) => r.data),
};

export const authApi = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
  logout: () => api.post('/auth/logout').then((r) => r.data),
};

export const salesApi = {
  list: (params) => api.get('/sales', { params }).then((r) => r.data),
  get: (id) => api.get(`/sales/${id}`).then((r) => r.data),
  create: (body) => api.post('/sales', body).then((r) => r.data),
  update: (id, body) => api.patch(`/sales/${id}`, body).then((r) => r.data),
  cancel: (id, reason) => api.post(`/sales/${id}/cancel`, { reason }).then((r) => r.data),
  addPayment: (id, body) => api.post(`/sales/${id}/payments`, body).then((r) => r.data),
};

export const adminApi = {
  getRaffle: () => api.get('/admin/raffle').then((r) => r.data),
  updateRaffle: (body) => api.put('/admin/raffle', body).then((r) => r.data),
  listUsers: () => api.get('/admin/users').then((r) => r.data),
  createUser: (body) => api.post('/admin/users', body).then((r) => r.data),
  updateUser: (id, body) => api.patch(`/admin/users/${id}`, body).then((r) => r.data),
  reports: () => api.get('/admin/reports').then((r) => r.data),
  reportsBySeller: () => api.get('/admin/reports/by-seller').then((r) => r.data),
  auditLogs: () => api.get('/admin/audit-logs').then((r) => r.data),
  overdue: () => api.get('/admin/overdue').then((r) => r.data),
  exportCsvUrl: () => `${API_URL}/api/admin/reports/export.csv`,
};

export const resultsApi = {
  list: () => api.get('/raffle/results').then((r) => r.data),
  create: (body) => api.post('/admin/raffle/results', body).then((r) => r.data),
  confirm: (id) => api.post(`/admin/raffle/results/${id}/confirm`).then((r) => r.data),
};

export default api;

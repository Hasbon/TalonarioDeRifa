import { useCallback, useEffect, useState } from 'react';
import { authApi } from '../services/api';

export function useAuth() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user') || 'null');
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(!!localStorage.getItem('access_token'));

  const refresh = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return null;
    }
    try {
      const me = await authApi.me();
      localStorage.setItem('user', JSON.stringify(me));
      setUser(me);
      return me;
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = async (username, password) => {
    const { access_token } = await authApi.login(username, password);
    localStorage.setItem('access_token', access_token);
    const me = await authApi.me();
    localStorage.setItem('user', JSON.stringify(me));
    setUser(me);
    return me;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignore */
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return { user, loading, login, logout, refresh, isAdmin: user?.role === 'admin' };
}

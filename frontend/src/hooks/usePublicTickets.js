import { useCallback, useEffect, useState } from 'react';
import { publicApi } from '../services/api';

const POLL_MS = 25000;

export function usePublicTickets() {
  const [tickets, setTickets] = useState([]);
  const [raffle, setRaffle] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [r, t] = await Promise.all([publicApi.getRaffle(), publicApi.getTickets()]);
      setRaffle(r);
      setTickets(t);
      setError(null);
    } catch (e) {
      setError(e.response?.data?.detail || 'No se pudo cargar la rifa');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, POLL_MS);
    return () => clearInterval(id);
  }, [load]);

  return { tickets, raffle, error, loading, reload: load };
}

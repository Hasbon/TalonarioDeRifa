import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { toPng } from 'html-to-image';
import BoletaCard from '../components/BoletaCard';
import { publicApi, salesApi } from '../services/api';
import '../components/BoletaCard.css';

export default function BoletaView() {
  const { saleId } = useParams();
  const ref = useRef(null);
  const [sale, setSale] = useState(null);
  const [raffle, setRaffle] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [captureMode, setCaptureMode] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [s, r] = await Promise.all([salesApi.get(saleId), publicApi.getRaffle()]);
        setSale(s);
        setRaffle(r);
      } catch (e) {
        setError(e.response?.data?.detail || 'No se pudo cargar la boleta');
      }
    })();
  }, [saleId]);

  const downloadPng = async () => {
    if (!ref.current) return;
    setBusy(true);
    try {
      const dataUrl = await toPng(ref.current, {
        cacheBust: true,
        pixelRatio: 2,
        backgroundColor: '#fffdf8',
      });
      const a = document.createElement('a');
      a.download = `boleta-${sale.number_code}.png`;
      a.href = dataUrl;
      a.click();
    } catch {
      setError('No se pudo generar el PNG');
    } finally {
      setBusy(false);
    }
  };

  const share = async () => {
    if (!ref.current || !navigator.share) {
      await downloadPng();
      return;
    }
    setBusy(true);
    try {
      const dataUrl = await toPng(ref.current, { cacheBust: true, pixelRatio: 2 });
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      const file = new File([blob], `boleta-${sale.number_code}.png`, { type: 'image/png' });
      await navigator.share({
        title: `Boleta ${sale.number_code}`,
        text: `Boleta ${sale.number_code} — ${raffle?.name || 'Rifa'}`,
        files: [file],
      });
    } catch {
      /* user cancelled or unsupported */
    } finally {
      setBusy(false);
    }
  };

  if (error && !sale) return <div className="alert alert-error">{error}</div>;
  if (!sale) return <p className="alert alert-info">Cargando boleta…</p>;

  return (
    <div className={`boleta-preview-page ${captureMode ? 'capture-mode' : ''}`}>
      {!captureMode && (
        <>
          <h1>Boleta digital {sale.number_code}</h1>
          {error && <div className="alert alert-error">{error}</div>}
          <div className="boleta-actions">
            <button type="button" className="btn btn-primary" onClick={downloadPng} disabled={busy}>
              Descargar PNG
            </button>
            <button type="button" className="btn btn-gold" onClick={share} disabled={busy}>
              Compartir
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setCaptureMode(true)}>
              Vista para captura
            </button>
            <Link className="btn btn-ghost" to={`/app/ventas/${sale.id}`}>
              Volver a la venta
            </Link>
          </div>
        </>
      )}
      {captureMode && (
        <button
          type="button"
          className="btn btn-ghost"
          style={{ marginBottom: '1rem' }}
          onClick={() => setCaptureMode(false)}
        >
          Salir de captura
        </button>
      )}
      <BoletaCard ref={ref} sale={sale} raffle={raffle} />
    </div>
  );
}

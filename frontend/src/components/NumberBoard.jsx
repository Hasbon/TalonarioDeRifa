import './NumberBoard.css';

export default function NumberBoard({ tickets, onSelect, interactive = false }) {
  if (!tickets?.length) {
    return <p className="board-empty">Cargando números…</p>;
  }

  return (
    <div className="number-board" role="list" aria-label="Tablero de números 00 a 99">
      {tickets.map((t) => {
        const cls = t.available ? 'cell available' : 'cell taken';
        const label = t.available ? 'Disponible' : 'No disponible';
        if (interactive) {
          return (
            <button
              key={t.number_code}
              type="button"
              className={cls}
              role="listitem"
              title={`${t.number_code}: ${label}`}
              aria-label={`Número ${t.number_code}, ${label}`}
              onClick={() => onSelect?.(t)}
              disabled={!t.available && !onSelect}
            >
              {t.number_code}
            </button>
          );
        }
        return (
          <div
            key={t.number_code}
            className={cls}
            role="listitem"
            title={`${t.number_code}: ${label}`}
            aria-label={`Número ${t.number_code}, ${label}`}
          >
            {t.number_code}
          </div>
        );
      })}
    </div>
  );
}

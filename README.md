# Rifa Digital — Talonario 00–99

Plataforma web completa para administrar una rifa de 100 números (00 al 99), con página pública, panel de vendedores, abonos, boletas digitales con QR, reportes y confirmación del resultado del sorteo.

**Idioma:** español · **Moneda:** COP · **Zona horaria:** America/Bogota  
**Sorteo configurado:** 30 de diciembre de 2026 · **Entrega:** 31 de diciembre de 2026, 10:00 a. m.

> **Aviso legal:** Antes de publicar o comercializar la rifa, verifique los requisitos aplicables en Colombia para rifas y juegos de suerte y azar, así como las obligaciones de protección de datos personales (Ley 1581 de 2012). Este software **no constituye autorización oficial**.

---

## Arquitectura

| Capa | Tecnología |
|------|------------|
| Frontend | React (Vite), React Router, CSS puro, Axios, `qrcode.react`, `html-to-image` |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, JWT + Argon2 |
| Base de datos | PostgreSQL (producción); SQLite opcional en desarrollo |

Frontend y backend se comunican **solo** mediante la API REST documentada en `/docs` (Swagger).

---

## Datos oficiales iniciales

- Premio: cerdo de 90 kg + garrafa de aguardiente  
- Alternativa: $1.200.000 COP  
- Precio boleta: $30.000 COP  
- Números: `00` … `99` (se conservan ceros a la izquierda)  
- Ganador: dos últimas cifras del premio mayor de la Lotería del Valle  

**Regla fundamental:** al asignar un número queda **ocupado aunque no haya pago completo**. No hay liberación automática por falta de pago ni por fecha de compromiso vencida. Solo un administrador puede anular con motivo auditado; el historial financiero se conserva.

---

## Requisitos

- Python 3.11+ (recomendado 3.12 para Docker)
- Node.js 20+
- Docker y Docker Compose (opcional, recomendado para PostgreSQL)

---

## Inicio rápido (desarrollo con SQLite)

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # o cp en Unix
# Ajuste SECRET_KEY en .env — nunca use el valor de ejemplo en producción

# Crear administrador (contraseña mín. 10 caracteres; NO hay clave débil por defecto)
python -m app.scripts.create_admin --username admin --full-name "Administrador"

# Arrancar API
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Abrir http://localhost:5173

### 3. Pruebas

```bash
cd backend
python -m pytest app/tests -v
```

---

## PostgreSQL con Docker Compose

```bash
# Desde la raíz del repositorio
docker compose up -d --build

# Crear admin contra la API en contenedor
docker compose exec api python -m app.scripts.create_admin --username admin --full-name "Administrador" --password "SuClaveSegura123"
```

Variables relevantes:

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | `postgresql+psycopg://rifa:rifa_secret@db:5432/rifa_digital` |
| `SECRET_KEY` | Secreto JWT (largo y aleatorio) |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma |
| `PUBLIC_BASE_URL` | Dominio público para enlaces QR de boletas |

### Migraciones Alembic

Con PostgreSQL activo:

```bash
cd backend
alembic upgrade head
```

En desarrollo con SQLite, `create_all` + seed al arrancar la app también inicializan el esquema y los 100 números.

---

## Roles

- **Administrador:** configuración, usuarios, anulación de ventas/pagos, resultados del sorteo, reportes CSV, auditoría.
- **Vendedor:** ventas, abonos, boletas, consulta de sus operaciones. No crea usuarios ni confirma resultados.

La autorización se valida en el **backend**; ocultar botones en React no es suficiente.

---

## Endpoints principales

- `POST /api/auth/login` · `GET /api/auth/me` · `POST /api/auth/logout`
- `GET /api/public/raffle` · `GET /api/public/tickets` · `GET /api/public/boletas/{token}`
- `GET|POST /api/sales` · `POST /api/sales/{id}/payments` · `POST /api/sales/{id}/cancel`
- `GET /api/admin/reports` · `GET /api/admin/audit-logs` · `GET /api/admin/users`
- `POST /api/admin/raffle/results` · `POST /api/admin/raffle/results/{id}/confirm`

La API pública **no** expone nombres, teléfonos, abonos ni datos de vendedores.

---

## Boletas y QR

Tras asignar un número, el vendedor genera una boleta digital con QR que apunta a:

`{PUBLIC_BASE_URL}/boleta/{token_publico}`

La validación consulta el estado actual en el backend. Si la venta fue anulada, la página muestra **anulada** aunque exista un PNG descargado previamente. La imagen no confirma el pago por sí sola.

---

## Copias de seguridad

```bash
# Backup
./scripts/backup_db.sh

# Restore
./scripts/restore_db.sh backups/rifa_digital_YYYYMMDD_HHMMSS.sql.gz
```

En Windows puede usar `docker compose exec -T db pg_dump -U rifa rifa_digital > backup.sql`.

---

## Producción (checklist)

1. PostgreSQL gestionado o Compose con volúmenes persistentes  
2. `SECRET_KEY` fuerte y único  
3. `CORS_ORIGINS` restringido al dominio real  
4. `PUBLIC_BASE_URL` con HTTPS  
5. Reverse proxy (Nginx/Caddy) con TLS  
6. `npm run build` del frontend y servir `frontend/dist`  
7. Crear admin con `create_admin` (sin contraseñas por defecto en el repo)  
8. Programar backups y probar restauración  
9. Cumplir requisitos legales y de Habeas Data antes de publicar  

---

## Estructura del repositorio

```
TalonarioRifas/
  backend/          # FastAPI
  frontend/         # React + Vite
  docker-compose.yml
  scripts/          # backup / restore
  README.md
```

---

## Criterio de aceptación (flujo)

1. Admin configura rifa 2026 y crea vendedores  
2. Vendedor inicia sesión, registra comprador y asigna número  
3. Número bloqueado sin pago completo; tablero público en rojo  
4. Abonos y saldo correctos; boleta PNG + QR válidos  
5. Anulación libera el número sin borrar historial  
6. Admin confirma resultado; ganador = dos últimas cifras del premio mayor  
7. Reportes y auditoría coherentes con la base de datos  

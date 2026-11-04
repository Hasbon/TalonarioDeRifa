# Despliegue: Firebase Hosting + Heroku

Arquitectura:

| Pieza | Plataforma | URL típica |
|-------|------------|------------|
| Frontend (React) | Firebase Hosting | `https://TU-PROYECTO.web.app` |
| API (FastAPI) | Heroku | `https://TU-APP.herokuapp.com` |
| Base de datos | Heroku Postgres | inyectada como `DATABASE_URL` |

> Heroku ya no tiene plan gratuito. Para un proyecto liviano suele bastar un **Eco dyno** + **Postgres Essential** (requiere tarjeta).

---

## Requisitos en tu PC

- Cuenta [Heroku](https://www.heroku.com) con facturación activa
- Cuenta Google + proyecto en [Firebase Console](https://console.firebase.google.com)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Node.js 20+ y `npm`
- Git
- PowerShell

```powershell
npm install -g firebase-tools
heroku --version
firebase --version
```

---

## Variables de entorno

### Heroku (API)

| Variable | Ejemplo | Notas |
|----------|---------|--------|
| `DATABASE_URL` | (automática) | La crea el add-on Postgres; el backend la normaliza a `postgresql+psycopg://` |
| `SECRET_KEY` | cadena larga aleatoria | **Obligatoria** en producción |
| `CORS_ORIGINS` | `https://TU-PROYECTO.web.app` | Origen exacto del front (sin barra final) |
| `PUBLIC_BASE_URL` | `https://TU-PROYECTO.web.app` | Base de enlaces QR de boletas |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Opcional |
| `TIMEZONE` | `America/Bogota` | Opcional |
| `LOGIN_RATE_LIMIT` | `10/minute` | Opcional |

### Frontend (build Vite)

Archivo: `frontend/.env.production` (partir de `.env.production.example`)

| Variable | Ejemplo |
|----------|---------|
| `VITE_API_URL` | `https://TU-APP.herokuapp.com` |
| `VITE_PUBLIC_BASE_URL` | `https://TU-PROYECTO.web.app` |

Estas se **incrustan en el build**. Si cambias la URL de la API, vuelve a hacer `npm run build` y `firebase deploy`.

---

## 1. Backend en Heroku (paso a paso)

### 1.1 Login y app

```powershell
cd "c:\Hasbon\Forja de codigo\TalonarioRifas"
heroku login
```

Desde la carpeta `backend` (ahí están `Procfile`, `runtime.txt` y `requirements.txt`):

```powershell
cd backend
heroku create talonario-rifas-api
```

Si el nombre está ocupado, elige otro. Anota la URL: `https://talonario-rifas-api-XXXX.herokuapp.com`.

Asocia el remoto Heroku si creaste la app desde la raíz del monorepo:

```powershell
# Desde la raíz del repo, si hace falta:
# heroku git:remote -a NOMBRE-DE-TU-APP
```

### 1.2 Postgres

```powershell
heroku addons:create heroku-postgresql:essential-0
heroku config | Select-String DATABASE_URL
```

### 1.3 Config vars

Genera un secreto (PowerShell):

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 48 | ForEach-Object { [char]$_ })
```

Luego (ajusta el nombre del proyecto Firebase cuando lo tengas; puedes poner un placeholder y actualizar después):

```powershell
heroku config:set SECRET_KEY="PEGA_AQUI_EL_SECRETO"
heroku config:set CORS_ORIGINS="https://TU-PROYECTO.web.app"
heroku config:set PUBLIC_BASE_URL="https://TU-PROYECTO.web.app"
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=60
heroku config:set TIMEZONE="America/Bogota"
```

### 1.4 Deploy del backend (monorepo)

El código de la API vive en `backend/`. Desde la **raíz** del repositorio:

```powershell
cd "c:\Hasbon\Forja de codigo\TalonarioRifas"

# Asegura que el remoto se llama heroku
heroku git:remote -a NOMBRE-DE-TU-APP

# Sube solo la carpeta backend a Heroku
git subtree push --prefix backend heroku main
```

Si tu rama local no se llama `main`:

```powershell
git subtree push --prefix backend heroku master
```

Si `subtree` falla por historial, alternativa:

```powershell
git push heroku `git subtree split --prefix backend main`:main --force
```

Tras el deploy, el `Procfile` ejecuta `alembic upgrade head` en la fase `release` y luego arranca Uvicorn.

### 1.5 Crear administrador

```powershell
heroku run python -m app.scripts.create_admin --username admin --full-name "Administrador"
```

Te pedirá la contraseña (mín. 10 caracteres) si no pasas `--password`.

### 1.6 Verificar API

```powershell
heroku open
# o en el navegador:
# https://NOMBRE-DE-TU-APP.herokuapp.com/health
# https://NOMBRE-DE-TU-APP.herokuapp.com/docs
```

```powershell
heroku logs --tail
```

---

## 2. Frontend en Firebase (paso a paso)

### 2.1 Proyecto Firebase

1. En [Firebase Console](https://console.firebase.google.com) → **Agregar proyecto** (ej. `talonario-rifas`).
2. Activa **Hosting** si el asistente lo pide (o al hacer el primer deploy).

### 2.2 Login y proyecto local

```powershell
cd "c:\Hasbon\Forja de codigo\TalonarioRifas"
firebase login
```

Edita [`.firebaserc`](.firebaserc) y reemplaza `TU-PROYECTO-FIREBASE` por el **Project ID** real de la consola:

```json
{
  "projects": {
    "default": "tu-project-id-real"
  }
}
```

O por CLI:

```powershell
firebase use tu-project-id-real
```

La config de Hosting ya está en [`firebase.json`](firebase.json): publica `frontend/dist` y reescribe rutas SPA a `index.html`.

### 2.3 Build de producción

```powershell
cd frontend
copy .env.production.example .env.production
notepad .env.production
```

Pon las URLs reales, por ejemplo:

```
VITE_API_URL=https://NOMBRE-DE-TU-APP.herokuapp.com
VITE_PUBLIC_BASE_URL=https://tu-project-id-real.web.app
```

```powershell
npm install
npm run build
cd ..
firebase deploy --only hosting
```

La CLI mostrará la URL: `https://tu-project-id-real.web.app`.

### 2.4 Cerrar el círculo (CORS y QR)

Cuando ya tengas la URL `.web.app` definitiva:

```powershell
heroku config:set CORS_ORIGINS="https://tu-project-id-real.web.app"
heroku config:set PUBLIC_BASE_URL="https://tu-project-id-real.web.app"
```

Si cambiaste `VITE_*`, vuelve a build + deploy del front:

```powershell
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

---

## 3. Checklist final

- [ ] `GET /health` en Heroku responde OK
- [ ] `/docs` carga Swagger
- [ ] `https://….web.app` muestra el tablero público (sin error CORS en DevTools)
- [ ] Login con el admin creado
- [ ] Una venta genera boleta cuyo QR apunta a `https://….web.app/boleta/...`
- [ ] `SECRET_KEY` no es el valor de ejemplo del repo

---

## Redeploy rápido (scripts)

Desde la raíz del repo en PowerShell (hace falta haber hecho **commit** de los cambios del backend):

```powershell
# Solo API → Heroku
.\scripts\deploy-api.ps1

# Solo frontend → Firebase
.\scripts\deploy-front.ps1

# Ambos
.\scripts\deploy-all.ps1
```

Si PowerShell bloquea la ejecución de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Notas:

- `deploy-api.ps1` exige working tree limpio (todo commiteado).
- `deploy-front.ps1` usa `frontend\.env.production` (no hace falta commit del front para Firebase).
- Si cambias `VITE_*`, hay que volver a correr `deploy-front.ps1`.

### Comandos útiles

```powershell
heroku config -a talonario-rifas-api
heroku logs --tail -a talonario-rifas-api
heroku restart -a talonario-rifas-api
```

---

## Archivos de despliegue en este repo

| Archivo | Rol |
|---------|-----|
| `scripts/deploy-api.ps1` | Redeploy backend a Heroku (subtree + token) |
| `scripts/deploy-front.ps1` | Build Vite + `firebase deploy --only hosting` |
| `scripts/deploy-all.ps1` | API + frontend |
| `backend/Procfile` | `release` (Alembic) + `web` (Uvicorn en `$PORT`) |
| `backend/runtime.txt` | Python 3.12 en Heroku |
| `backend/app/core/config.py` | Normaliza `DATABASE_URL` de Heroku |
| `firebase.json` | Hosting SPA → `frontend/dist` |
| `.firebaserc` | Project ID de Firebase |
| `frontend/.env.production.example` | Plantilla de variables Vite |

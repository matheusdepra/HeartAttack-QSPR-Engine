# CardioQSPR Frontend

React + Vite interface for the CardioQSPR academic QSPR platform.

## Requirements

- Node.js 20 or newer
- Backend running on `http://localhost:5555`

## Install

```bash
npm install
```

## Development

```bash
npm run dev
```

Open `http://localhost:5173`.

## Build Check

```bash
npm run build
```

The production bundle is written to `dist/`.

## Configuration

The UI reads Vite environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_HOST` | unset | Explicit backend host override |
| `VITE_API_PORT` | `5555` | Backend API port |
| `VITE_API_PREFIX` | `/api` | Backend API prefix |
| `VITE_STATIC_PREFIX` | `/plots` | Backend static plot prefix |
| `VITE_LOCAL_API_HOST` | `http://localhost` | Local API host |
| `VITE_STORAGE_USER_KEY` | `cardio_user` | Login storage key |
| `VITE_APP_NAME` | `CardioQSPR` | Display name |
| `VITE_APP_SHORT_NAME` | `CQ` | Compact display name |
| `VITE_APP_VERSION` | `v1.0` | Version label |

For the standard local setup, no frontend `.env` file is required.

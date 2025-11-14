# Setup Guide

## Prerequisites

- Python 3.11+
- Poetry 1.8+
- Node.js 18+ (Vite and shadcn-ui depend on modern ESM features)
- npm 9+
- Redis (optional for future event streaming)
- PostgreSQL (not required for the current in-memory prototype)

## Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

The API will be accessible at `http://localhost:8000`. Interactive docs are available at `/docs`.

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Description |
| --- | --- |
| `PROJECT_SIGNALS_ALLOWED_ORIGINS` | Comma-separated list of allowed origins |
| `PROJECT_SIGNALS_WEBHOOK_SECRETS__CHARTINK_TOKEN` | Shared token for Chartink alerts |
| `PROJECT_SIGNALS_WEBHOOK_SECRETS__TRADINGVIEW_TOKEN` | Shared token for TradingView alerts |

## Frontend Console

```bash
cd frontend
npm install
npm run dev
```

- Development server: `http://localhost:5173`
- Configure an alternate backend endpoint by adding `.env` in `frontend/` with `VITE_API_BASE_URL=http://your-backend:8000`.
- shadcn-ui components are defined under `src/components/ui`. Utility helpers live in `src/lib`.

### Frontend Testing

```bash
cd frontend
npm run test -- --run
```

Vitest stubs backend calls with mock responses. For end-to-end validation point the console at a running backend and exercise flows manually.

## Webhook Configuration

- **Chartink**: Set the webhook URL to `http://<host>:8000/api/v1/webhooks/chartink` and include a custom header `X-Chartink-Token` with the configured secret.
- **TradingView**: Configure webhook to `http://<host>:8000/api/v1/webhooks/tradingview` with header `X-TradingView-Token`.

Payloads are currently stored in-memory and can be extended to publish to Redis streams for asynchronous processing.

## Testing

```bash
poetry run pytest
```

## Next Steps

- Persist instruments, orders, and account snapshots to PostgreSQL
- Expand simulation engine with derivatives-specific margin and fee models
- Implement event-driven strategy execution using Celery workers
- Integrate live NSE/BSE market data adapters
- Add authentication and multi-tenant account support



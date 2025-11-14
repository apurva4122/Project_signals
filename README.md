# Project Signals

Project Signals is a modular paper trading and backtesting platform tailored for Indian equities, futures, and options markets. It provides a FastAPI backend, strategy execution engine, market data adapters, and webhook integrations for Chartink and TradingView signals.

## Features

- FastAPI backend exposing REST endpoints for instruments, accounts, orders, and backtests
- Simulation engine for paper trading with configurable strategies
- Backtesting pipeline leveraging Polars and mock CSV data feeds
- Webhook ingestion endpoints with token validation for Chartink and TradingView
- Service registry pattern for dependency management and future extension to live data vendors

## Getting Started

### Backend API

```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000` with interactive docs available at `/docs`.

### Frontend Console (React + Vite + shadcn-ui)

```bash
cd frontend
npm install
npm run dev
```

The development server runs on `http://localhost:5173` and expects the backend to be available at `http://localhost:8000` by default. Set `VITE_API_BASE_URL` in a `.env` file inside `frontend/` to point to another backend.

### Tests

- Backend: `cd backend && poetry run pytest`
- Frontend: `cd frontend && npm run test -- --run`

See `docs/setup.md` for extended configuration notes, webhook instructions, and troubleshooting tips.



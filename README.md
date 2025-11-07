# Project Signals

Project Signals is a modular paper trading and backtesting platform tailored for Indian equities, futures, and options markets. It provides a FastAPI backend, strategy execution engine, market data adapters, and webhook integrations for Chartink and TradingView signals.

## Features

- FastAPI backend exposing REST endpoints for instruments, accounts, orders, and backtests
- Simulation engine for paper trading with configurable strategies
- Backtesting pipeline leveraging Polars and mock CSV data feeds
- Webhook ingestion endpoints with token validation for Chartink and TradingView
- Service registry pattern for dependency management and future extension to live data vendors

## Getting Started

```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload
```

Frontend scaffolding is pending; refer to `docs/architecture.md` for system design details.

Additional setup guidance and webhook configuration steps are available in `docs/setup.md`.



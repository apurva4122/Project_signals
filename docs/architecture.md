## Overview

Project Signals is a modular paper-trading and backtesting platform tailored for Indian equities, equity futures, and options. The platform provides:

- A unified market data abstraction layer with adapters for NSE/BSE cash instruments and NSE derivatives via third-party data vendors.
- A deterministic simulation engine capable of both streaming paper trades and historical backtesting runs.
- Strategy execution services with plug-in support for Python-based strategies, webhook-driven signal ingestion (Chartink, TradingView), and scheduled rule execution.
- A responsive web interface, inspired by AlgoTest, for configuring strategies, monitoring trades, and inspecting performance metrics.
- Extensible integrations for order routing (simulated), risk management, and trade analytics.

## High-Level Architecture

```
┌──────────────────────────────┐
│          Frontend            │
│  (React + Vite + Chakra UI)  │
└──────────────┬───────────────┘
               │ GraphQL/REST
┌──────────────▼───────────────┐
│         API Gateway          │
│       (FastAPI, uvicorn)     │
└──────────────┬───────────────┘
               │
 ┌─────────────┼────────────────────────────────────────────────────────────┐
 │             │                                                            │
 │   ┌─────────▼────────┐      ┌───────────────────────┐    ┌────────────┐  │
 │   │ Strategy Engine  │◀────▶│  Portfolio Service    │◀──▶│ Risk Rules │  │
 │   │   (Celery,       │      │  (positions, P&L)     │    │            │  │
 │   │    Pydantic)     │      └───────────────────────┘    └────────────┘  │
 │   └─────────┬────────┘                 ▲                   ▲             │
 │             │                          │                   │             │
 │   ┌─────────▼────────┐      ┌──────────┴─────────┐         │             │
 │   │ Market Data Hub  │─────▶│   Simulation Core   │────────┘             │
 │   │ (async adapters) │      │ (order fills, pnl)  │                       │
 │   └─────────┬────────┘      └──────────┬─────────┘                       │
 │             │                          │                                 │
 │   ┌─────────▼────────┐      ┌──────────▼─────────┐                       │
 │   │ Webhook Ingress  │─────▶│ Event Bus (Redis)  │                       │
 │   │ (Chartink/TV)    │      │                   │                       │
 │   └──────────────────┘      └────────────────────┘                       │
 └──────────────────────────────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────┐
│   Data Store Layer           │
│ (PostgreSQL, Redis, MinIO)   │
└──────────────────────────────┘
```

### Key Components

- **Frontend**: React-based SPA built with Vite and Chakra UI, communicating via REST/GraphQL. Provides dashboards, strategy configuration, trade blotter, and charting (via lightweight charts / TradingView lightweight library).
- **API Gateway**: FastAPI application exposing REST endpoints and websocket streams. Handles authentication, validation, routing to services, and documentation (Swagger/OpenAPI).
- **Market Data Hub**: Pluggable adapters for NSE/BSE cash and derivatives. Each adapter conforms to a common interface and can source data from vendors such as Zerodha Kite Connect, Upstox, or Algoseek. In development mode, CSV/Parquet mocks are provided.
- **Simulation Core**: Implements order matching, fill simulation, transaction cost modeling (brokerage, STT, GST), lot size enforcement, and margin calculations for Indian derivatives markets.
- **Strategy Engine**: Executes strategies defined as Python classes or via external signals. Supports scheduled jobs (Celery beat) or event-driven execution. Provides factories for signal translation from webhooks.
- **Portfolio Service**: Maintains virtual accounts, positions, cash balances, and P&L (realized/unrealized). Generates trade ledger and contract notes.
- **Risk Rules**: Configurable pre-trade and post-trade checks (max exposure, stop loss, hedge requirements, option greeks limits).
- **Webhook Ingress**: Receives Chartink and TradingView webhook payloads, validates HMAC signatures, maps to internal strategy identifiers, and queues signals for execution.
- **Data Store Layer**: PostgreSQL for transactional data, Redis for caching/event bus, MinIO/S3 for historical data storage, and optional DuckDB/Parquet for local analytics.

## Backend Services

### FastAPI Application

- `app/main.py`: entrypoint, includes routers for authentication, instruments, market data, strategies, orders, and analytics.
- `app/dependencies.py`: shared dependencies (db sessions, redis clients).
- `app/routers`: modular route definitions.
- `app/schemas`: Pydantic models for request/response validation.
- `app/services`: business logic (market data service, order execution service, backtest runner).
- `app/workers`: Celery tasks, event consumers.

### Simulation Engine

- `core/execution/order_book.py`: Manages simulated order books per instrument.
- `core/execution/fills.py`: Fill algorithms (market, limit, stop, IOC, option-specific rules).
- `core/risk/margin.py`: Indian margin models (SPAN, exposure).
- `core/risk/fees.py`: Brokerage templates for Zerodha/Upstox/Fyers, taxes, exchange fees.
- `core/portfolio/accounts.py`: Account state handling.
- `core/backtesting/runner.py`: Historical backtest orchestrator using pandas/numba/polars.

### Market Data Adapters

- `adapters/marketdata/base.py`: Abstract base class.
- `adapters/marketdata/mock_csv.py`: Local CSV-based feed for development.
- `adapters/marketdata/zerodha.py`: Kite Connect integration (placeholder).
- `adapters/marketdata/chartink.py`: Signal translation.

### Strategy Templates

- `strategies/base.py`: Base Strategy API (hooks: `on_init`, `on_tick`, `on_bar`, `on_signal`).
- `strategies/example_mean_reversion.py`: Sample strategy showing pair trading on NIFTY stocks.
- `strategies/options_short_straddle.py`: Options example with risk controls.

## Webhook Integrations

### Chartink

- Accepts POST payloads defined by Chartink alert webhooks.
- Validates secret token and optional HMAC signature.
- Maps symbols to NSE/BSE codes via instrument master.
- Enqueues signal with desired action, quantity, additional metadata.

### TradingView

- Receives TradingView webhook JSON, supporting both simple alerts and PineScript custom payloads.
- Optional JWT for authentication.
- Supports multi-leg instructions (e.g., straddle entry) encoded in JSON.
- Publishes to Redis stream for asynchronous processing by strategy engine.

## Data Model (Preliminary)

- **Instrument**: symbol, exchange, segment (EQ, FUT, OPT), lot size, tick size, expiry, strike, option type.
- **Strategy**: name, type (`python`, `webhook`), parameters, linked virtual account.
- **Order**: strategy_id, instrument_id, side, order_type, qty, price, status, fills.
- **Fill**: order_id, trade_id, fill_price, fill_qty, fees.
- **Position**: instrument_id, net_qty, average_price, realized_pnl, unrealized_pnl.
- **Account**: cash_balance, margin_used, collateral, ledger entries.
- **Signal**: source, payload, mapped strategy, timestamp, status.
- **Backtest**: configuration, metrics, result artifacts (equity curve, trades list).

## Deployment Overview

- Docker Compose orchestrating services: `api`, `frontend`, `worker`, `redis`, `postgres`, `minio`.
- CI/CD pipeline with linting (ruff, mypy), testing (pytest), frontend lint/tests (eslint/jest), and packaging.
- Production deployment via Kubernetes or managed container services; uses environment-specific configuration.

## Next Steps

1. Scaffold FastAPI backend and core domain modules.
2. Implement mock market data adapter and basic paper trading simulation.
3. Provide REST endpoints for instruments, accounts, orders, backtests.
4. Build minimal frontend skeleton mirroring AlgoTest layout (dashboard, strategy builder, blotter).
5. Integrate webhook ingestion endpoints and queue processing.
6. Add historical backtesting engine leveraging Polars or Pandas with zipped Parquet data.
7. Implement authentication (JWT) and multi-tenant account separation.
8. Set up automated tests and continuous integration workflows.



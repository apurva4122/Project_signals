"""Dependency exports for FastAPI."""

from .dependencies import (
    get_backtesting_service,
    get_instruments_service,
    get_registry,
    get_settings_dep,
    get_trading_service,
    get_webhook_service,
)

__all__ = [
    "get_backtesting_service",
    "get_instruments_service",
    "get_registry",
    "get_settings_dep",
    "get_trading_service",
    "get_webhook_service",
]



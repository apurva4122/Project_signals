"""API dependency providers."""

from functools import lru_cache
from pathlib import Path

from ...config import get_settings
from ...config.settings import AppSettings
from ...services.registry import ServiceRegistry
from ...services import BacktestingService, InstrumentsService, TradingService
from ...services.webhooks import WebhookService


@lru_cache(maxsize=1)
def _get_registry() -> ServiceRegistry:
    settings = get_settings()
    return ServiceRegistry.from_settings(settings)


def get_settings_dep() -> AppSettings:
    return get_settings()


def get_registry() -> ServiceRegistry:
    return _get_registry()


def get_trading_service() -> TradingService:
    return _get_registry().trading_service


def get_backtesting_service() -> BacktestingService:
    return _get_registry().backtesting_service


def get_instruments_service() -> InstrumentsService:
    return _get_registry().instruments_service


def get_webhook_service() -> WebhookService:
    return _get_registry().webhook_service



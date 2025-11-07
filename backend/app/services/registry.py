"""Service registry for dependency management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ...core import BacktestRunner, PortfolioManager, SimulationEngine
from ...core.data import MarketDataProvider, MockCSVMarketData
from ..config.settings import AppSettings
from .backtesting import BacktestingService
from .instruments import InstrumentsService
from .trading import TradingService
from .webhooks import WebhookService


@dataclass(slots=True)
class ServiceRegistry:
    settings: AppSettings
    _portfolio_manager: PortfolioManager = field(init=False)
    _market_data_provider: MarketDataProvider = field(init=False)
    _simulation_engine: SimulationEngine = field(init=False)
    _backtest_runner: BacktestRunner = field(init=False)
    _trading_service: TradingService = field(init=False)
    _backtesting_service: BacktestingService = field(init=False)
    _instrument_service: InstrumentsService = field(init=False)
    _webhook_service: WebhookService = field(init=False)

    def __post_init__(self) -> None:
        self._ensure_data_dirs()
        self._portfolio_manager = PortfolioManager()
        self._market_data_provider = self._create_market_data_provider()
        self._simulation_engine = SimulationEngine(self._portfolio_manager)
        self._backtest_runner = BacktestRunner(self._market_data_provider)
        self._instrument_service = InstrumentsService(storage_path=Path(self.settings.data_path) / "instruments")
        self._trading_service = TradingService(self._simulation_engine)
        self._backtesting_service = BacktestingService(self._backtest_runner)
        self._webhook_service = WebhookService()

    def _ensure_data_dirs(self) -> None:
        for path in [self.settings.data_path, self.settings.historical_cache_path]:
            Path(path).mkdir(parents=True, exist_ok=True)

    def _create_market_data_provider(self) -> MarketDataProvider:
        mock_dir = Path(self.settings.data_path) / "mock"
        mock_dir.mkdir(parents=True, exist_ok=True)
        return MockCSVMarketData(data_dir=mock_dir)

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "ServiceRegistry":
        return cls(settings=settings)

    @property
    def simulation_engine(self) -> SimulationEngine:
        return self._simulation_engine

    @property
    def backtest_runner(self) -> BacktestRunner:
        return self._backtest_runner

    @property
    def portfolio_manager(self) -> PortfolioManager:
        return self._portfolio_manager

    @property
    def market_data_provider(self) -> MarketDataProvider:
        return self._market_data_provider

    @property
    def trading_service(self) -> TradingService:
        return self._trading_service

    @property
    def backtesting_service(self) -> BacktestingService:
        return self._backtesting_service

    @property
    def instruments_service(self) -> InstrumentsService:
        return self._instrument_service

    @property
    def webhook_service(self) -> WebhookService:
        return self._webhook_service



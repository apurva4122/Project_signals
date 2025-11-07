"""Historical backtesting runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List

import polars as pl

from ..data import MarketDataEvent, MarketDataProvider
from ..execution.engine import SimulationEngine, SimulationOrder, SimulationResult
from ..portfolio.account import AccountState, PortfolioManager


@dataclass(slots=True)
class BacktestConfig:
    strategy_id: str
    symbols: list[str]
    start: datetime
    end: datetime
    initial_capital: float = 10_00_000.0
    order_generator: Iterable[SimulationOrder] | None = None


@dataclass(slots=True)
class BacktestResult:
    config: BacktestConfig
    equity_curve: pl.DataFrame
    trades: list[SimulationResult]
    final_state: AccountState

    @property
    def total_return(self) -> float:
        start_value = self.config.initial_capital
        end_value = self.final_state.cash_balance
        return (end_value - start_value) / start_value


class BacktestRunner:
    """Executes backtests using a market data provider and simulation engine."""

    def __init__(self, data_provider: MarketDataProvider) -> None:
        self.data_provider = data_provider

    def run(self, config: BacktestConfig) -> BacktestResult:
        portfolio = PortfolioManager(AccountState(cash_balance=config.initial_capital))
        engine = SimulationEngine(portfolio)
        trades: list[SimulationResult] = []
        equity_points: list[dict[str, float | datetime]] = []

        for symbol in config.symbols:
            historical = self.data_provider.historical(symbol, config.start, config.end)
            for event in historical:
                for result in engine.process_market_data(event):
                    trades.append(result)
                equity_points.append(
                    {
                        "timestamp": event.timestamp,
                        "cash_balance": portfolio.state.cash_balance,
                    }
                )

        if config.order_generator is not None:
            for order in config.order_generator:
                trades.append(engine.submit_order(order, market_price=0.0))

        equity_df = pl.DataFrame(equity_points) if equity_points else pl.DataFrame({"timestamp": [], "cash_balance": []})
        return BacktestResult(
            config=config,
            equity_curve=equity_df,
            trades=trades,
            final_state=portfolio.state,
        )



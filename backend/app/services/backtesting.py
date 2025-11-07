"""Backtesting service for orchestrating historical simulations."""

from __future__ import annotations

from datetime import datetime

from ..schemas.backtests import BacktestRequest, BacktestResponse, BacktestMetrics
from ...core.backtesting.runner import BacktestConfig
from ...core import BacktestRunner


class BacktestingService:
    def __init__(self, runner: BacktestRunner) -> None:
        self.runner = runner

    def run_backtest(self, request: BacktestRequest) -> BacktestResponse:
        config = BacktestConfig(
            strategy_id=request.strategy_id,
            symbols=request.symbols,
            start=request.start,
            end=request.end,
            initial_capital=request.initial_capital,
        )
        result = self.runner.run(config)
        metrics = BacktestMetrics(
            total_return=result.total_return,
            final_equity=result.final_state.cash_balance,
        )
        return BacktestResponse(backtest_id=f"BT-{datetime.utcnow().timestamp()}", metrics=metrics)



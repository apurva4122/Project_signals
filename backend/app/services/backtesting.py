"""Backtesting service for orchestrating historical simulations."""

from __future__ import annotations

from datetime import datetime

import numpy as np

from ..schemas.backtests import BacktestRequest, BacktestResponse, BacktestMetrics, LegResult
from core.backtesting.runner import BacktestConfig
from core import BacktestRunner


class BacktestingService:
    def __init__(self, runner: BacktestRunner) -> None:
        self.runner = runner

    def run_backtest(self, request: BacktestRequest) -> BacktestResponse:
        # Convert leg configs to dict format for runner
        legs = None
        if request.legs:
            legs = [leg.model_dump() for leg in request.legs]

        config = BacktestConfig(
            strategy_id=request.strategy_id,
            symbols=request.symbols,
            start=request.start,
            end=request.end,
            initial_capital=request.initial_capital,
            legs=legs,
        )
        result = self.runner.run(config)

        # Calculate enhanced metrics
        total_trades = len(result.trades)
        winning_trades = sum(1 for trade in result.trades if trade.status.value == "FILLED" and len(trade.fills) > 0)
        losing_trades = total_trades - winning_trades

        # Calculate max drawdown from equity curve
        max_drawdown = 0.0
        sharpe_ratio = 0.0
        if not result.equity_curve.is_empty() and "cash_balance" in result.equity_curve.columns:
            equity_values = result.equity_curve["cash_balance"].to_numpy()
            if len(equity_values) > 1:
                running_max = np.maximum.accumulate(equity_values)
                drawdowns = (equity_values - running_max) / running_max
                max_drawdown = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0

                # Simple Sharpe ratio (assuming risk-free rate = 0)
                returns = np.diff(equity_values) / equity_values[:-1]
                if len(returns) > 0 and np.std(returns) > 0:
                    sharpe_ratio = float(np.mean(returns) / np.std(returns) * np.sqrt(252))  # Annualized

        metrics = BacktestMetrics(
            total_return=result.total_return,
            final_equity=result.final_state.cash_balance,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
        )

        # Build leg results if legs were used
        leg_results = None
        if request.legs and result.trades:
            leg_results = self._extract_leg_results(request.legs, result.trades)

        return BacktestResponse(
            backtest_id=f"BT-{datetime.utcnow().timestamp()}",
            metrics=metrics,
            leg_results=leg_results,
        )

    def _extract_leg_results(self, leg_configs: list, trades: list) -> list[LegResult]:
        """Extract leg-wise results from trades."""
        results = []
        for leg_cfg in leg_configs:
            leg_dict = leg_cfg.model_dump() if hasattr(leg_cfg, "model_dump") else leg_cfg
            # Find entry and exit trades for this leg
            entry_trades = [t for t in trades if t.order.symbol == leg_dict["symbol"] and t.order.side.value == leg_dict["side"]]
            exit_trades = [
                t
                for t in trades
                if t.order.symbol == leg_dict["symbol"]
                and t.order.side.value != leg_dict["side"]
            ]

            entry_price = 0.0
            exit_price = None
            if entry_trades and entry_trades[0].fills:
                entry_price = entry_trades[0].fills[0].fill_price
            if exit_trades and exit_trades[-1].fills:
                exit_price = exit_trades[-1].fills[-1].fill_price

            pnl = 0.0
            if exit_price is not None:
                if leg_dict["side"] == "BUY":
                    pnl = (exit_price - entry_price) * leg_dict["quantity"]
                else:
                    pnl = (entry_price - exit_price) * leg_dict["quantity"]

            results.append(
                LegResult(
                    symbol=leg_dict["symbol"],
                    side=leg_dict["side"],
                    quantity=leg_dict["quantity"],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    pnl=pnl,
                    exit_reason=None,  # Can be enhanced to track from leg state
                )
            )
        return results



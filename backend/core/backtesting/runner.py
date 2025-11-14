"""Historical backtesting runner with leg logic support."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List

import polars as pl

from ..data import MarketDataEvent, MarketDataProvider
from ..execution.engine import SimulationEngine, SimulationOrder, SimulationResult
from ..execution.models import OrderSide, OrderType
from ..portfolio.account import AccountState, PortfolioManager


@dataclass(slots=True)
class LegState:
    """Tracks the state of an active leg during backtesting."""

    symbol: str
    side: str
    quantity: int
    entry_price: float
    entry_time: datetime
    exit_target: float | None = None
    exit_stop_loss: float | None = None
    trailing_stop_points: float | None = None
    trailing_stop_percent: float | None = None
    highest_price: float | None = None
    lowest_price: float | None = None
    partial_square_off_percent: float | None = None
    time_based_exit_minutes: int | None = None
    remaining_quantity: int = 0
    exit_reason: str | None = None
    exit_price: float | None = None

    def __post_init__(self) -> None:
        self.remaining_quantity = self.quantity
        if self.side == "BUY":
            self.highest_price = self.entry_price
            self.lowest_price = self.entry_price
        else:
            self.highest_price = self.entry_price
            self.lowest_price = self.entry_price

    def update_price(self, current_price: float) -> None:
        """Update highest/lowest prices for trailing stop calculation."""
        if self.side == "BUY":
            if self.highest_price is None or current_price > self.highest_price:
                self.highest_price = current_price
            if self.lowest_price is None or current_price < self.lowest_price:
                self.lowest_price = current_price
        else:  # SELL
            if self.lowest_price is None or current_price < self.lowest_price:
                self.lowest_price = current_price
            if self.highest_price is None or current_price > self.highest_price:
                self.highest_price = current_price

    def should_exit(self, current_price: float, current_time: datetime) -> tuple[bool, str | None, float | None]:
        """Check if leg should exit based on configured conditions. Returns (should_exit, reason, exit_price)."""
        price_diff = current_price - self.entry_price
        if self.side == "SELL":
            price_diff = -price_diff

        # Target exit
        if self.exit_target is not None and price_diff >= self.exit_target:
            exit_qty = self.remaining_quantity
            if self.partial_square_off_percent is not None:
                exit_qty = int(self.remaining_quantity * (self.partial_square_off_percent / 100.0))
            if exit_qty > 0:
                return True, "TARGET", current_price

        # Stop loss exit
        if self.exit_stop_loss is not None and price_diff <= -self.exit_stop_loss:
            return True, "STOP_LOSS", current_price

        # Trailing stop (points)
        if self.trailing_stop_points is not None and self.highest_price is not None:
            if self.side == "BUY" and current_price <= (self.highest_price - self.trailing_stop_points):
                return True, "TRAILING_STOP", current_price
            if self.side == "SELL" and current_price >= (self.lowest_price + self.trailing_stop_points):
                return True, "TRAILING_STOP", current_price

        # Trailing stop (percentage)
        if self.trailing_stop_percent is not None and self.highest_price is not None:
            if self.side == "BUY" and current_price <= (self.highest_price * (1 - self.trailing_stop_percent / 100.0)):
                return True, "TRAILING_STOP", current_price
            if self.side == "SELL" and current_price >= (self.lowest_price * (1 + self.trailing_stop_percent / 100.0)):
                return True, "TRAILING_STOP", current_price

        # Time-based exit
        if self.time_based_exit_minutes is not None:
            elapsed = (current_time - self.entry_time).total_seconds() / 60.0
            if elapsed >= self.time_based_exit_minutes:
                return True, "TIME_BASED", current_price

        return False, None, None

    def calculate_pnl(self, exit_price: float) -> float:
        """Calculate P&L for this leg."""
        if self.side == "BUY":
            return (exit_price - self.entry_price) * self.quantity
        return (self.entry_price - exit_price) * self.quantity


@dataclass(slots=True)
class BacktestConfig:
    strategy_id: str
    symbols: list[str]
    start: datetime
    end: datetime
    initial_capital: float = 10_00_000.0
    order_generator: Iterable[SimulationOrder] | None = None
    legs: list[dict] | None = None  # List of leg configurations


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
    """Executes backtests using a market data provider and simulation engine with leg logic support."""

    def __init__(self, data_provider: MarketDataProvider) -> None:
        self.data_provider = data_provider

    def run(self, config: BacktestConfig) -> BacktestResult:
        portfolio = PortfolioManager(AccountState(cash_balance=config.initial_capital))
        engine = SimulationEngine(portfolio)
        trades: list[SimulationResult] = []
        equity_points: list[dict[str, float | datetime]] = []
        active_legs: list[LegState] = []

        # Initialize legs if provided
        if config.legs:
            for leg_cfg in config.legs:
                # Legs will be entered when entry conditions are met during data processing
                pass

        # Process historical data
        for symbol in config.symbols:
            historical = self.data_provider.historical(symbol, config.start, config.end)
            for event in historical:
                # Process market data for pending orders
                for result in engine.process_market_data(event):
                    trades.append(result)

                # Handle leg logic if legs are configured
                if config.legs:
                    self._process_leg_logic(
                        event, config, active_legs, engine, trades, portfolio
                    )

                equity_points.append(
                    {
                        "timestamp": event.timestamp,
                        "cash_balance": portfolio.state.cash_balance,
                    }
                )

        # Close any remaining active legs at end
        if active_legs:
            for leg in active_legs:
                if leg.remaining_quantity > 0 and leg.exit_price is None:
                    # Force exit at last known price
                    last_price = leg.highest_price or leg.entry_price
                    if leg.side == "SELL":
                        last_price = leg.lowest_price or leg.entry_price
                    self._exit_leg(leg, last_price, "END_OF_BACKTEST", engine, trades, portfolio)

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

    def _process_leg_logic(
        self,
        event: MarketDataEvent,
        config: BacktestConfig,
        active_legs: list[LegState],
        engine: SimulationEngine,
        trades: list[SimulationResult],
        portfolio: PortfolioManager,
    ) -> None:
        """Process leg entry and exit logic based on market data."""
        if not config.legs:
            return

        # Check for leg entries
        for leg_cfg in config.legs:
            if leg_cfg["symbol"] != event.symbol:
                continue

            # Check if leg is already active
            is_active = any(
                leg.symbol == leg_cfg["symbol"]
                and leg.side == leg_cfg["side"]
                and leg.remaining_quantity > 0
                for leg in active_legs
            )

            if not is_active:
                # Simple entry: enter immediately (entry_condition can be extended later)
                leg_state = LegState(
                    symbol=leg_cfg["symbol"],
                    side=leg_cfg["side"],
                    quantity=leg_cfg["quantity"],
                    entry_price=event.price,
                    entry_time=event.timestamp,
                    exit_target=leg_cfg.get("exit_target"),
                    exit_stop_loss=leg_cfg.get("exit_stop_loss"),
                    trailing_stop_points=leg_cfg.get("trailing_stop_points"),
                    trailing_stop_percent=leg_cfg.get("trailing_stop_percent"),
                    partial_square_off_percent=leg_cfg.get("partial_square_off_percent"),
                    time_based_exit_minutes=leg_cfg.get("time_based_exit_minutes"),
                )
                active_legs.append(leg_state)

                # Submit entry order
                order = SimulationOrder(
                    order_id=f"LEG-{len(active_legs)}-ENTRY",
                    symbol=leg_cfg["symbol"],
                    side=OrderSide.BUY if leg_cfg["side"] == "BUY" else OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=leg_cfg["quantity"],
                    timestamp=event.timestamp,
                    strategy_id=config.strategy_id,
                )
                result = engine.submit_order(order, market_price=event.price)
                trades.append(result)

        # Check for leg exits
        legs_to_remove: list[LegState] = []
        for leg in active_legs:
            if leg.symbol != event.symbol or leg.remaining_quantity <= 0:
                continue

            leg.update_price(event.price)
            should_exit, reason, exit_price = leg.should_exit(event.price, event.timestamp)

            if should_exit and exit_price is not None:
                self._exit_leg(leg, exit_price, reason or "UNKNOWN", engine, trades, portfolio)
                if leg.remaining_quantity <= 0:
                    legs_to_remove.append(leg)

        for leg in legs_to_remove:
            active_legs.remove(leg)

    def _exit_leg(
        self,
        leg: LegState,
        exit_price: float,
        reason: str,
        engine: SimulationEngine,
        trades: list[SimulationResult],
        portfolio: PortfolioManager,
    ) -> None:
        """Exit a leg by submitting opposite order."""
        if leg.remaining_quantity <= 0:
            return

        exit_side = OrderSide.SELL if leg.side == "BUY" else OrderSide.BUY
        order = SimulationOrder(
            order_id=f"LEG-{leg.symbol}-{leg.side}-EXIT",
            symbol=leg.symbol,
            side=exit_side,
            order_type=OrderType.MARKET,
            quantity=leg.remaining_quantity,
            timestamp=datetime.utcnow(),
            strategy_id="leg-strategy",
        )
        result = engine.submit_order(order, market_price=exit_price)
        trades.append(result)

        leg.exit_price = exit_price
        leg.exit_reason = reason
        leg.remaining_quantity = 0



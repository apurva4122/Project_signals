"""Backtest request and response schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LegExitType(str, Enum):
    """Exit condition types for strategy legs."""

    TARGET = "TARGET"
    STOP_LOSS = "STOP_LOSS"
    TRAILING_STOP = "TRAILING_STOP"
    TIME_BASED = "TIME_BASED"
    PARTIAL_SQUARE_OFF = "PARTIAL_SQUARE_OFF"


class LegConfig(BaseModel):
    """Configuration for a single strategy leg."""

    symbol: str = Field(..., description="Trading symbol for this leg")
    side: str = Field(..., description="BUY or SELL")
    quantity: int = Field(..., gt=0, description="Quantity for this leg")
    entry_condition: str | None = Field(default=None, description="Optional entry condition expression")
    exit_target: float | None = Field(default=None, description="Target profit in points/percentage")
    exit_stop_loss: float | None = Field(default=None, description="Stop loss in points/percentage")
    trailing_stop_points: float | None = Field(default=None, description="Trailing stop in points")
    trailing_stop_percent: float | None = Field(default=None, description="Trailing stop in percentage")
    partial_square_off_percent: float | None = Field(default=None, ge=0, le=100, description="Partial square-off percentage at target")
    time_based_exit_minutes: int | None = Field(default=None, gt=0, description="Time-based exit in minutes from entry")


class BacktestRequest(BaseModel):
    strategy_id: str
    symbols: list[str]
    start: datetime
    end: datetime
    initial_capital: float = Field(default=10_00_000.0)
    legs: list[LegConfig] | None = Field(default=None, description="Multi-leg strategy configuration")


class BacktestMetrics(BaseModel):
    total_return: float
    final_equity: float
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0


class LegResult(BaseModel):
    """Result metrics for a single leg."""

    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float | None = None
    pnl: float = 0.0
    exit_reason: str | None = None


class BacktestResponse(BaseModel):
    backtest_id: str
    metrics: BacktestMetrics
    leg_results: list[LegResult] | None = None



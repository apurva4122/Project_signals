"""Backtest request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    strategy_id: str
    symbols: list[str]
    start: datetime
    end: datetime
    initial_capital: float = Field(default=10_00_000.0)


class BacktestMetrics(BaseModel):
    total_return: float
    final_equity: float


class BacktestResponse(BaseModel):
    backtest_id: str
    metrics: BacktestMetrics



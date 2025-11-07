"""Base strategy definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from ..core.data import MarketDataEvent
from ..core.execution.engine import SimulationOrder


@dataclass(slots=True)
class StrategyContext:
    strategy_id: str
    symbols: list[str]


class Strategy(Protocol):
    def on_init(self, context: StrategyContext) -> None: ...

    def on_tick(self, context: StrategyContext, event: MarketDataEvent) -> list[SimulationOrder]: ...

    def on_signal(self, context: StrategyContext, payload: dict[str, Any]) -> list[SimulationOrder]: ...



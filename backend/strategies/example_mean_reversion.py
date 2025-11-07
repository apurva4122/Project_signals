"""Example mean reversion strategy template."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from statistics import mean
from typing import Deque, List

from ..core.data import MarketDataEvent
from ..core.execution.engine import OrderSide, OrderType, SimulationOrder
from .base import StrategyContext


@dataclass(slots=True)
class MeanReversionStrategy:
    lookback: int = 20
    qty: int = 1
    _prices: Deque[float] = field(default_factory=lambda: deque(maxlen=20))

    def on_init(self, context: StrategyContext) -> None:  # pragma: no cover - placeholder
        self._prices = deque(maxlen=self.lookback)

    def on_tick(self, context: StrategyContext, event: MarketDataEvent) -> List[SimulationOrder]:
        orders: list[SimulationOrder] = []
        self._prices.append(event.price)
        if len(self._prices) < self.lookback:
            return orders
        avg_price = mean(self._prices)
        if event.price < avg_price * 0.995:
            orders.append(
                SimulationOrder(
                    order_id=f"MR-{context.strategy_id}-{event.timestamp.timestamp()}",
                    symbol=event.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=self.qty,
                    price=event.price,
                    timestamp=event.timestamp,
                    strategy_id=context.strategy_id,
                )
            )
        elif event.price > avg_price * 1.005:
            orders.append(
                SimulationOrder(
                    order_id=f"MR-{context.strategy_id}-{event.timestamp.timestamp()}",
                    symbol=event.symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=self.qty,
                    price=event.price,
                    timestamp=event.timestamp,
                    strategy_id=context.strategy_id,
                )
            )
        return orders

    def on_signal(self, context: StrategyContext, payload: dict) -> List[SimulationOrder]:
        return []



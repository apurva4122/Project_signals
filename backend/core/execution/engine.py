"""Simulation engine for paper trading and backtesting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable, List, Optional

from ..portfolio.account import AccountState, PortfolioManager
from ..data import MarketDataEvent


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass(slots=True)
class SimulationOrder:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: float | None = None
    timestamp: datetime | None = None
    strategy_id: str | None = None
    metadata: dict[str, str] | None = None


@dataclass(slots=True)
class SimulationFill:
    order_id: str
    fill_id: str
    symbol: str
    fill_price: float
    quantity: int
    timestamp: datetime


@dataclass(slots=True)
class SimulationResult:
    order: SimulationOrder
    status: OrderStatus
    fills: List[SimulationFill] = field(default_factory=list)
    message: str | None = None


class SimulationEngine:
    """Core engine for processing simulated orders and market data"""

    def __init__(
        self,
        portfolio: PortfolioManager,
        latency_ms: int = 0,
    ) -> None:
        self.portfolio = portfolio
        self.latency_ms = latency_ms
        self.pending_orders: dict[str, SimulationOrder] = {}

    def submit_order(self, order: SimulationOrder, market_price: float) -> SimulationResult:
        """Simulate order execution assuming immediate-or-cancel semantics for now"""

        fills: list[SimulationFill] = []
        status = OrderStatus.REJECTED
        message: str | None = None

        if order.quantity <= 0:
            message = "Quantity must be positive"
            return SimulationResult(order=order, status=status, fills=fills, message=message)

        execution_price = self._determine_fill_price(order, market_price)
        if execution_price is None:
            status = OrderStatus.PENDING
            self.pending_orders[order.order_id] = order
            message = "Order parked in book awaiting trigger"
            return SimulationResult(order=order, status=status, fills=fills, message=message)

        fill = SimulationFill(
            order_id=order.order_id,
            fill_id=f"{order.order_id}-1",
            symbol=order.symbol,
            fill_price=execution_price,
            quantity=order.quantity,
            timestamp=datetime.utcnow(),
        )
        fills.append(fill)
        status = OrderStatus.FILLED

        self.portfolio.apply_fill(fill, order.side)

        return SimulationResult(order=order, status=status, fills=fills, message=message)

    def _determine_fill_price(self, order: SimulationOrder, market_price: float) -> float | None:
        if order.order_type == OrderType.MARKET:
            return market_price
        if order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and order.price is not None and order.price >= market_price:
                return float(order.price)
            if order.side == OrderSide.SELL and order.price is not None and order.price <= market_price:
                return float(order.price)
            return None
        if order.order_type == OrderType.STOP:
            if order.side == OrderSide.BUY and order.price is not None and market_price >= order.price:
                return market_price
            if order.side == OrderSide.SELL and order.price is not None and market_price <= order.price:
                return market_price
            return None
        return market_price

    def process_market_data(self, event: MarketDataEvent) -> list[SimulationResult]:
        """Attempt to fill pending orders when market data arrives"""

        to_remove: list[str] = []
        results: list[SimulationResult] = []
        for order_id, order in list(self.pending_orders.items()):
            if order.symbol != event.symbol:
                continue
            fill_price = self._determine_fill_price(order, event.price)
            if fill_price is None:
                continue
            fill = SimulationFill(
                order_id=order.order_id,
                fill_id=f"{order.order_id}-{len(results)+1}",
                symbol=order.symbol,
                fill_price=fill_price,
                quantity=order.quantity,
                timestamp=event.timestamp,
            )
            self.portfolio.apply_fill(fill, order.side)
            results.append(
                SimulationResult(order=order, status=OrderStatus.FILLED, fills=[fill])
            )
            to_remove.append(order_id)

        for order_id in to_remove:
            self.pending_orders.pop(order_id, None)

        return results

    def reset(self, account_state: Optional[AccountState] = None) -> None:
        self.pending_orders.clear()
        if account_state:
            self.portfolio.reset(account_state)



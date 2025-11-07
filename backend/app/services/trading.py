"""Trading service orchestrating simulation engine interactions."""

from __future__ import annotations

from datetime import datetime
from typing import Tuple

from ..schemas.orders import OrderRequest, OrderResponse
from ...core.execution.engine import SimulationOrder
from ...core import SimulationEngine


class TradingService:
    def __init__(self, engine: SimulationEngine) -> None:
        self.engine = engine

    def submit_order(self, request: OrderRequest) -> OrderResponse:
        order = SimulationOrder(
            order_id=f"ORD-{datetime.utcnow().timestamp()}",
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
            timestamp=datetime.utcnow(),
            strategy_id=request.strategy_id,
        )
        result = self.engine.submit_order(order, market_price=request.price or 0.0)
        filled_quantity = sum(fill.quantity for fill in result.fills)
        avg_price = (
            sum(fill.fill_price * fill.quantity for fill in result.fills) / filled_quantity
            if filled_quantity
            else None
        )
        return OrderResponse(
            order_id=order.order_id,
            status=result.status,
            filled_quantity=filled_quantity,
            avg_fill_price=avg_price,
            timestamp=order.timestamp or datetime.utcnow(),
        )



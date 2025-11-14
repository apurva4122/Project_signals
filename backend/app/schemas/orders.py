"""Order request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from core.execution.models import OrderSide, OrderStatus, OrderType


class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    quantity: int
    price: float | None = None
    strategy_id: str | None = Field(default=None, description="Associated strategy")


class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    filled_quantity: int
    avg_fill_price: float | None
    timestamp: datetime



"""Shared execution data structures and enumerations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


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



"""Portfolio and account state management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..execution.engine import OrderSide, SimulationFill


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0

    def apply_fill(self, fill: SimulationFill, side: OrderSide) -> None:
        signed_qty = fill.quantity if side == OrderSide.BUY else -fill.quantity
        new_total = self.quantity + signed_qty
        if new_total == 0:
            self.quantity = 0
            self.avg_price = 0.0
            return
        if (self.quantity >= 0 and signed_qty >= 0) or (self.quantity <= 0 and signed_qty <= 0):
            total_cost = self.avg_price * abs(self.quantity) + fill.fill_price * fill.quantity
            self.quantity = new_total
            self.avg_price = total_cost / abs(self.quantity)
        else:
            self.quantity = new_total
            if self.quantity == 0:
                self.avg_price = 0.0


@dataclass(slots=True)
class AccountState:
    cash_balance: float = 10_00_000.0
    margin_used: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)


class PortfolioManager:
    """Manages account state, positions, and cashflows"""

    def __init__(self, state: AccountState | None = None) -> None:
        self.state = state or AccountState()

    def reset(self, state: AccountState | None = None) -> None:
        self.state = state or AccountState()

    def apply_fill(self, fill: SimulationFill, side: OrderSide) -> None:
        position = self.state.positions.setdefault(fill.symbol, Position(symbol=fill.symbol))
        position.apply_fill(fill, side)
        cash_delta = fill.fill_price * fill.quantity
        if side == OrderSide.BUY:
            self.state.cash_balance -= cash_delta
        else:
            self.state.cash_balance += cash_delta

    def get_position(self, symbol: str) -> Position | None:
        return self.state.positions.get(symbol)



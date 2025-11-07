"""Account schemas for API responses."""

from pydantic import BaseModel


class PositionSchema(BaseModel):
    symbol: str
    quantity: int
    avg_price: float


class AccountSnapshot(BaseModel):
    cash_balance: float
    margin_used: float
    positions: list[PositionSchema]



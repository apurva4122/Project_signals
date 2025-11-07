"""Instrument schemas."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class InstrumentSegment(str, Enum):
    EQUITY = "EQ"
    FUTURES = "FUT"
    OPTIONS = "OPT"


class Instrument(BaseModel):
    symbol: str = Field(..., description="Trading symbol, e.g., RELIANCE")
    exchange: str = Field(default="NSE")
    segment: InstrumentSegment = InstrumentSegment.EQUITY
    lot_size: int | None = Field(default=None, description="Lot size for derivatives")
    tick_size: float = 0.05
    expiry: date | None = None
    strike: float | None = None
    option_type: str | None = Field(default=None, description="CE/PE for options")


class InstrumentCreate(BaseModel):
    symbol: str
    exchange: str = "NSE"
    segment: InstrumentSegment = InstrumentSegment.EQUITY
    lot_size: int | None = None
    tick_size: float = 0.05
    expiry: date | None = None
    strike: float | None = None
    option_type: str | None = None



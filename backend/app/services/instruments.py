"""Instruments service to manage instrument metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from ..schemas.instruments import Instrument, InstrumentCreate


class InstrumentsService:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Instrument] = {}

    def list_instruments(self) -> list[Instrument]:
        return list(self._cache.values())

    def upsert_instrument(self, payload: InstrumentCreate) -> Instrument:
        instrument = Instrument(**payload.model_dump())
        self._cache[instrument.symbol] = instrument
        return instrument



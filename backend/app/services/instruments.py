"""Instruments service to manage instrument metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable

from core.data.providers.motilal import MotilalMarketData

from ..schemas.instruments import Instrument, InstrumentCreate, InstrumentSegment


class InstrumentsService:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Instrument] = {}
        self._cache_file = self.storage_path / "instruments.json"
        self._load_cache()

    def list_instruments(self) -> list[Instrument]:
        if not self._cache and self._cache_file.exists():
            self._load_cache()
        return sorted(self._cache.values(), key=lambda inst: inst.symbol)

    def upsert_instrument(self, payload: InstrumentCreate) -> Instrument:
        instrument = Instrument(**payload.model_dump())
        self._cache[instrument.symbol] = instrument
        self._persist_cache()
        return instrument

    def refresh_from_motilal(self, provider: MotilalMarketData, symbols: Iterable[str]) -> list[Instrument]:
        instruments: list[Instrument] = []
        for symbol in symbols:
            try:
                meta = provider.get_instrument_metadata(symbol)
            except Exception as exc:  # pylint: disable=broad-except
                continue
            instrument = Instrument(
                symbol=meta["symbol"],
                exchange="NSE",
                segment=InstrumentSegment.EQUITY,
                lot_size=None,
                tick_size=0.05,
            )
            self._cache[instrument.symbol] = instrument
            instruments.append(instrument)
        self._persist_cache()
        return instruments

    def _load_cache(self) -> None:
        if not self._cache_file.exists():
            return
        with self._cache_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for item in payload:
            instrument = Instrument(**item)
            self._cache[instrument.symbol] = instrument

    def _persist_cache(self) -> None:
        with self._cache_file.open("w", encoding="utf-8") as handle:
            json.dump([instr.model_dump() for instr in self._cache.values()], handle, indent=2)



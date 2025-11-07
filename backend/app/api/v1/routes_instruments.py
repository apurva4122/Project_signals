"""Instrument endpoints."""

from fastapi import APIRouter, Depends

from ...schemas.instruments import Instrument, InstrumentCreate
from ..deps.dependencies import get_instruments_service

router = APIRouter()


@router.get("/", response_model=list[Instrument])
def list_instruments(service=Depends(get_instruments_service)) -> list[Instrument]:
    return service.list_instruments()


@router.post("/", response_model=Instrument)
def upsert_instrument(
    payload: InstrumentCreate,
    service=Depends(get_instruments_service),
) -> Instrument:
    return service.upsert_instrument(payload)



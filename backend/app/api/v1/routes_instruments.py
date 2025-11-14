"""Instrument endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...schemas.instruments import Instrument, InstrumentCreate
from ..deps.dependencies import get_instruments_service, get_motilal_service, get_settings_dep
from ...services.brokers import MotilalBrokerService
from core.data.providers.motilal import MotilalMarketData
from ...config.settings import AppSettings

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


@router.post("/refresh/nifty100", response_model=list[Instrument])
def refresh_nifty100(
    instrument_service=Depends(get_instruments_service),
    motilal_service: MotilalBrokerService = Depends(get_motilal_service),
    settings: AppSettings = Depends(get_settings_dep),
) -> list[Instrument]:
    raw = motilal_service.get_raw_credentials()
    if not raw or not raw.get("auth_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Motilal credentials are not configured.",
        )
    provider = MotilalMarketData(
        credentials=raw,
        api_base=settings.motilal.api_base,
        timeout_seconds=settings.motilal.timeout_seconds,
        interval_minutes=settings.motilal.historical_interval_minutes,
        lookback_days=settings.motilal.historical_lookback_days,
    )
    try:
        symbols = provider.get_nifty100_symbols()
        instruments = instrument_service.refresh_from_motilal(provider, symbols)
        return instruments
    finally:
        provider.close()


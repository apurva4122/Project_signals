"""Webhook ingestion endpoints for Chartink and TradingView."""

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status

from ..deps.dependencies import get_settings_dep, get_webhook_service

router = APIRouter()


@router.post("/chartink", status_code=status.HTTP_202_ACCEPTED)
def ingest_chartink(
    payload: dict[str, Any],
    token: str | None = Header(default=None, alias="X-Chartink-Token"),
    service=Depends(get_webhook_service),
    settings=Depends(get_settings_dep),
) -> dict[str, str]:
    expected = settings.webhook_secrets.chartink_token
    if expected and expected != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Chartink token")
    event = service.ingest("chartink", payload)
    return {"status": "accepted", "received_at": event.received_at.isoformat()}


@router.post("/tradingview", status_code=status.HTTP_202_ACCEPTED)
def ingest_tradingview(
    payload: dict[str, Any],
    token: str | None = Header(default=None, alias="X-TradingView-Token"),
    service=Depends(get_webhook_service),
    settings=Depends(get_settings_dep),
) -> dict[str, str]:
    expected = settings.webhook_secrets.tradingview_token
    if expected and expected != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TradingView token")
    event = service.ingest("tradingview", payload)
    return {"status": "accepted", "received_at": event.received_at.isoformat()}



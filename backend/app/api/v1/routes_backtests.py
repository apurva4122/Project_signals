"""Backtest endpoints."""

from fastapi import APIRouter, Depends, status

from ...schemas.backtests import BacktestRequest, BacktestResponse
from ..deps.dependencies import get_backtesting_service

router = APIRouter()


@router.post("/", response_model=BacktestResponse, status_code=status.HTTP_202_ACCEPTED)
def run_backtest(request: BacktestRequest, service=Depends(get_backtesting_service)) -> BacktestResponse:
    return service.run_backtest(request)



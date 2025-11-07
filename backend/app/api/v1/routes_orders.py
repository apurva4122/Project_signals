"""Order endpoints."""

from fastapi import APIRouter, Depends, status

from ...schemas.orders import OrderRequest, OrderResponse
from ..deps.dependencies import get_trading_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(request: OrderRequest, service=Depends(get_trading_service)) -> OrderResponse:
    return service.submit_order(request)



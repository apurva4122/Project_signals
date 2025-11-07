"""Account endpoints."""

from fastapi import APIRouter, Depends

from ...schemas.accounts import AccountSnapshot, PositionSchema
from ..deps.dependencies import get_registry

router = APIRouter()


@router.get("/primary", response_model=AccountSnapshot)
def get_primary_account(registry=Depends(get_registry)) -> AccountSnapshot:
    portfolio = registry.portfolio_manager
    positions = [
        PositionSchema(symbol=pos.symbol, quantity=pos.quantity, avg_price=pos.avg_price)
        for pos in portfolio.state.positions.values()
    ]
    return AccountSnapshot(
        cash_balance=portfolio.state.cash_balance,
        margin_used=portfolio.state.margin_used,
        positions=positions,
    )



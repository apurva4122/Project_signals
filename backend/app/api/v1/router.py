"""API v1 route aggregator."""

from fastapi import APIRouter

from . import routes_accounts, routes_backtests, routes_health, routes_instruments, routes_orders, routes_webhooks

router = APIRouter()
router.include_router(routes_health.router, prefix="/health", tags=["health"])
router.include_router(routes_instruments.router, prefix="/instruments", tags=["instruments"])
router.include_router(routes_accounts.router, prefix="/accounts", tags=["accounts"])
router.include_router(routes_orders.router, prefix="/orders", tags=["orders"])
router.include_router(routes_backtests.router, prefix="/backtests", tags=["backtests"])
router.include_router(routes_webhooks.router, prefix="/webhooks", tags=["webhooks"])



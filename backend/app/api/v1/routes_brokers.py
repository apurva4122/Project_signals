"""Broker credential management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...schemas.brokers import MotilalConnectionStatus, MotilalCredentialsIn, MotilalCredentialsOut
from ..deps import get_motilal_service
from ...services.brokers import MotilalBrokerService

router = APIRouter()


@router.get("/motilal", response_model=MotilalCredentialsOut | None)
def read_motilal_credentials(service: MotilalBrokerService = Depends(get_motilal_service)) -> MotilalCredentialsOut | None:
    return service.get_credentials()


@router.post("/motilal", response_model=MotilalCredentialsOut, status_code=status.HTTP_201_CREATED)
def upsert_motilal_credentials(
    payload: MotilalCredentialsIn,
    service: MotilalBrokerService = Depends(get_motilal_service),
) -> MotilalCredentialsOut:
    return service.save_credentials(payload)


@router.get("/motilal/status", response_model=MotilalConnectionStatus)
async def motilal_status(service: MotilalBrokerService = Depends(get_motilal_service)) -> MotilalConnectionStatus:
    status_payload = await service.validate_connection()
    if not status_payload.connected:
        # surface validation failure details through HTTP error but include payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=status_payload.message or "Unable to validate Motilal credentials.",
        )
    return status_payload



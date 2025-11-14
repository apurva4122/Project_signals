"""Broker credential schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, SecretStr


class MotilalCredentialsIn(BaseModel):
    api_key: str = Field(..., description="Motilal Oswal API key issued to the client.")
    client_code: str = Field(..., description="Client code / user id registered with Motilal Oswal.")
    auth_token: SecretStr = Field(..., description="Active auth token obtained from Motilal Oswal login flow.")
    totp_secret: Optional[SecretStr] = Field(
        default=None,
        description="Optional TOTP secret for automating token refresh.",
    )


class MotilalCredentialsOut(BaseModel):
    api_key: str
    client_code: str
    has_auth_token: bool
    has_totp_secret: bool
    updated_at: datetime


class MotilalConnectionStatus(BaseModel):
    broker: str = "motilal"
    connected: bool
    message: str | None = None
    updated_at: datetime | None = None



"""Broker integration services."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

from ..config.settings import AppSettings
from ..schemas.brokers import MotilalConnectionStatus, MotilalCredentialsIn, MotilalCredentialsOut


class MotilalBrokerService:
    """Persist and validate Motilal Oswal API credentials."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._credentials_path: Path = settings.motilal_credentials_file

    def save_credentials(self, payload: MotilalCredentialsIn) -> MotilalCredentialsOut:
        data = {
            "api_key": payload.api_key,
            "client_code": payload.client_code,
            "auth_token": payload.auth_token.get_secret_value(),
            "totp_secret": payload.totp_secret.get_secret_value() if payload.totp_secret else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._credentials_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        return MotilalCredentialsOut(
            api_key=payload.api_key,
            client_code=payload.client_code,
            has_auth_token=True,
            has_totp_secret=payload.totp_secret is not None,
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def get_credentials(self) -> MotilalCredentialsOut | None:
        if not self._credentials_path.exists():
            return None
        with self._credentials_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return MotilalCredentialsOut(
            api_key=data["api_key"],
            client_code=data["client_code"],
            has_auth_token=bool(data.get("auth_token")),
            has_totp_secret=bool(data.get("totp_secret")),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def _read_raw_credentials(self) -> dict[str, Any] | None:
        if not self._credentials_path.exists():
            return None
        with self._credentials_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def get_raw_credentials(self) -> dict[str, Any] | None:
        return self._read_raw_credentials()

    def connection_status(self) -> MotilalConnectionStatus:
        creds = self.get_credentials()
        if not creds:
            return MotilalConnectionStatus(
                connected=False,
                message="Motilal credentials not configured.",
                updated_at=None,
            )
        if not creds.has_auth_token:
            return MotilalConnectionStatus(
                connected=False,
                message="Auth token missing. Please login via Motilal portal and update token.",
                updated_at=creds.updated_at,
            )
        return MotilalConnectionStatus(
            connected=True,
            message="Credentials stored locally.",
            updated_at=creds.updated_at,
        )

    async def validate_connection(self) -> MotilalConnectionStatus:
        raw = self._read_raw_credentials()
        if not raw:
            return MotilalConnectionStatus(connected=False, message="Credentials missing.", updated_at=None)
        headers = self._build_headers(raw)

        url = f"{self._settings.motilal.api_base}/rest/login/v3/getprofile"
        try:
            async with httpx.AsyncClient(timeout=self._settings.motilal.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json={"clientcode": raw["client_code"]})
                response.raise_for_status()
                payload = response.json()
                if payload.get("status") == "SUCCESS":
                    return MotilalConnectionStatus(
                        connected=True,
                        message="Motilal connection verified.",
                        updated_at=datetime.fromisoformat(raw["updated_at"]),
                    )
                return MotilalConnectionStatus(
                    connected=False,
                    message=payload.get("message") or "Motilal validation failed.",
                    updated_at=datetime.fromisoformat(raw["updated_at"]),
                )
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Motilal connection validation failed: {}", exc)
            return MotilalConnectionStatus(
                connected=False,
                message=f"Validation error: {exc}",
                updated_at=datetime.fromisoformat(raw["updated_at"]),
            )

    def _build_headers(self, raw_creds: dict[str, Any]) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "ApiKey": raw_creds["api_key"],
            "Authorization": raw_creds["auth_token"],
            "ClientLocalIp": raw_creds.get("client_local_ip", "127.0.0.1"),
            "ClientPublicIp": raw_creds.get("client_public_ip", "127.0.0.1"),
            "MacAddress": raw_creds.get("mac_address", "00:00:00:00:00:00"),
            "SourceId": raw_creds.get("source_id", "WEB"),
            "vendorinfo": raw_creds.get("vendor_info", raw_creds["client_code"]),
            "osname": raw_creds.get("os_name", "Windows"),
            "osversion": raw_creds.get("os_version", "10"),
            "browsername": raw_creds.get("browser_name", "Chrome"),
            "browserversion": raw_creds.get("browser_version", "119"),
            "User-Agent": "ProjectSignals/1.0",
        }

    def build_headers(self) -> dict[str, str]:
        raw = self._read_raw_credentials()
        if not raw:
            raise RuntimeError("Motilal credentials not configured.")
        return self._build_headers(raw)



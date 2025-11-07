"""Webhook handling services for external signal providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass(slots=True)
class WebhookEvent:
    source: str
    payload: Dict[str, Any]
    received_at: datetime


class WebhookService:
    def __init__(self) -> None:
        self._events: List[WebhookEvent] = []

    def ingest(self, source: str, payload: Dict[str, Any]) -> WebhookEvent:
        event = WebhookEvent(source=source, payload=payload, received_at=datetime.utcnow())
        self._events.append(event)
        return event

    def recent_events(self, limit: int = 50) -> list[WebhookEvent]:
        return list(self._events[-limit:])



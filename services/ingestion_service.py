from __future__ import annotations

from typing import Optional, Tuple

from django.db import transaction

from apps.devices.models import Device, Event
from tasks.ingestion_tasks import process_event_async


class IngestionService:
    @staticmethod
    @transaction.atomic
    def create_event(
        device_id: str,
        payload: dict,
        timestamp,
        event_type: str,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[Event, bool]:
        if idempotency_key:
            existing = Event.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return existing, False

        device = Device.objects.select_related("factory").get(device_id=device_id, is_active=True)

        event = Event.objects.create(
            device=device,
            factory=device.factory,
            payload=payload,
            timestamp=timestamp,
            event_type=event_type,
            idempotency_key=idempotency_key,
        )
        process_event_async.delay(event.id)
        return event, True

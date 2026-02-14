from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import Factory, Machine


class Device(models.Model):
    """IoT device sending telemetry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)

    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True)

    device_id = models.CharField(max_length=100, unique=True, db_index=True)

    device_type = models.CharField(max_length=100)
    last_seen_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)

    metadata = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.device_id} ({self.device_type})"


class Event(models.Model):
    """Time-series event data (partitioned by month)."""

    id = models.BigAutoField(primary_key=True)

    device = models.ForeignKey(Device, on_delete=models.CASCADE, db_index=True)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, db_index=True)

    timestamp = models.DateTimeField(db_index=True)
    event_type = models.CharField(max_length=50, db_index=True)
    payload = models.JSONField()

    idempotency_key = models.CharField(max_length=100, unique=True, null=True)

    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "timestamp"]),
            models.Index(fields=["device", "timestamp"]),
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.timestamp.isoformat()}"

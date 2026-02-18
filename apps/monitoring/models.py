from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import Factory, Machine


class Shift(models.Model):
    """Shift configuration"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
        ]
        unique_together = [["factory", "name"]]

    def __str__(self) -> str:
        return f"{self.factory.code}:{self.name}"


class DowntimeReason(models.Model):
    """Categorized downtime reasons"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    description = models.TextField()
    category = models.CharField(max_length=100)  # Mechanical,Electrical,Material, etc.
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
            models.Index(fields=["factory", "category"]),
        ]
        unique_together = [["factory", "code"]]

    def __str__(self) -> str:
        return f"{self.factory.code}:{self.code}"


class DowntimeLog(models.Model):
    """Recorded downtime incidents"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, db_index=True)
    reason = models.ForeignKey(DowntimeReason, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True)
    duration_minutes = models.IntegerField(null=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "started_at"]),
            models.Index(fields=["machine", "started_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.machine_id} downtime @ {self.started_at.isoformat()}"

from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import Factory


class AlertRule(models.Model):
    """Configurable alert thresholds"""

    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    metric_name = models.CharField(max_length=100)
    condition = models.CharField(
        max_length=20,
        choices=[("gt", ">"), ("lt", "<"), ("eq", "=")],
    )
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    severity = models.CharField(
        max_length=20,
        choices=[("info", "Info"), ("warning", "Warning"), ("critical", "Critical")],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
            models.Index(fields=["factory", "metric_name"]),
        ]
        unique_together = [["factory", "name"]]

    def __str__(self) -> str:
        return f"{self.factory.code}:{self.name}"


class Alert(models.Model):
    """Triggered alerts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, db_index=True)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=20,
        choices=[("open", "Open"), ("ack", "Acknowledged"), ("resolved", "Resolved")],
    )
    message = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["factory", "status", "triggered_at"]),
        ]

    def __str__(self) -> str:
        return f"Alert({self.status}) {self.triggered_at.date()}"

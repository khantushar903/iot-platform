from __future__ import annotations

import uuid

from django.contrib.auth.models import User
from django.db import models


class Factory(models.Model):
    """Top-level tenant boundary"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, db_index=True)

    timezone = models.CharField(max_length=50, default="Asia/Dhaka")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Line(models.Model):
    """Production line within a factory"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name="lines")

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    capacity_per_hour = models.IntegerField(null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
        ]
        unique_together = [["factory", "code"]]

    def __str__(self) -> str:
        return f"{self.factory.code}:{self.code}"


class Machine(models.Model):
    """Individual machine/workstation"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="machines")

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    machine_type = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["line", "is_active"]),
        ]
        unique_together = [["line", "code"]]

    def __str__(self) -> str:
        return f"{self.line}:{self.code}"


class Operator(models.Model):
    """Factory floor operator"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name="operators")

    employee_id = models.CharField(max_length=50, unique=True)

    name = models.CharField(max_length=200)

    skill_level = models.IntegerField(
        choices=[
            (1, "Trainee"),
            (2, "Junior"),
            (3, "Senior"),
            (4, "Expert"),
        ]
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["factory", "is_active"]),
            models.Index(fields=["employee_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.name}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} - {self.model}"

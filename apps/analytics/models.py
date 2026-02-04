from __future__ import annotations

from django.db import models

from apps.core.models import Factory, Line, Machine, Operator
from apps.monitoring.models import Shift


class KPISnapshot(models.Model):
    """Pre-aggregated KPI values"""

    id = models.BigAutoField(primary_key=True)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, db_index=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, null=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, null=True)
    snapshot_date = models.DateField(db_index=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True)

    total_production = models.IntegerField(default=0)
    target_production = models.IntegerField(default=0)
    efficiency_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    uptime_minutes = models.IntegerField(default=0)
    downtime_minutes = models.IntegerField(default=0)
    defect_count = models.IntegerField(default=0)
    cycle_time_avg_seconds = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["factory", "snapshot_date"]),
            models.Index(fields=["line", "snapshot_date"]),
            models.Index(fields=["machine", "snapshot_date"]),
        ]
        unique_together = [
            ["factory", "line", "machine", "operator", "snapshot_date", "shift"]
        ]

    def __str__(self) -> str:
        return f"KPI {self.snapshot_date} (factory={self.factory_id})"

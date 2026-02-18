from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from django.db.models import Avg, DecimalField, IntegerField, Sum
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone

from apps.analytics.models import KPISnapshot
from apps.core.models import Factory, Line
from apps.devices.models import Event
from apps.monitoring.models import DowntimeLog


@dataclass(frozen=True)
class LineKPIResult:
    total_production: int
    target_production: int
    efficiency_percent: Optional[Decimal]
    downtime_minutes: int
    cycle_time_avg_seconds: Optional[Decimal]


class KPIService:
    @staticmethod
    def _get_day_range(factory_tz: str, day: date) -> Tuple[datetime, datetime]:
        tz = ZoneInfo(factory_tz)

        start_local = datetime.combine(day, time.min).replace(tzinfo=tz)
        end_local = start_local + timedelta(days=1)

        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        return start_utc, end_utc

    @staticmethod
    def calculate_line_kpis(line_id, day: date) -> LineKPIResult:
        line = Line.objects.select_related("factory").get(id=line_id)
        factory: Factory = line.factory

        start_utc, end_utc = KPIService._get_day_range(factory.timezone, day)

        qs = Event.objects.filter(
            factory_id=factory.id,
            timestamp__gte=start_utc,
            timestamp__lt=end_utc,
            event_type="production_cycle",
            device__machine__line_id=line.id,
        )

        output_count_expr = Cast(
            KeyTextTransform("output_count", "payload"),
            output_field=IntegerField(),
        )

        cycle_time_expr = Cast(
            KeyTextTransform("cycle_time_seconds", "payload"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )

        agg = qs.aggregate(
            total_output=Coalesce(Sum(output_count_expr), 0, output_field=IntegerField()),
            avg_cycle=Avg(cycle_time_expr),
        )
        total_production = int(agg["total_output"] or 0)

        target_production = int((line.capacity_per_hour or 0) * 24)

        efficiency_percent: Optional[Decimal] = None
        if target_production > 0:
            efficiency_percent = (Decimal(total_production) / Decimal(target_production)) * Decimal(
                "100"
            )

        downtime_agg = DowntimeLog.objects.filter(
            factory_id=factory.id,
            machine__line_id=line.id,
            started_at__gte=start_utc,
            started_at__lt=end_utc,
        ).aggregate(total_down=Coalesce(Sum("duration_minutes"), 0))

        downtime_minutes = int(downtime_agg["total_down"] or 0)

        return LineKPIResult(
            total_production=total_production,
            target_production=target_production,
            efficiency_percent=efficiency_percent,
            downtime_minutes=downtime_minutes,
            cycle_time_avg_seconds=agg["avg_cycle"],
        )

    @staticmethod
    def generate_kpi_snapshots(factory_id, day: date) -> int:
        factory = Factory.objects.get(id=factory_id)

        lines = Line.objects.filter(factory_id=factory.id, is_active=True).only(
            "id", "factory_id", "capacity_per_hour"
        )

        snapshots: list[KPISnapshot] = []

        for line in lines:
            result = KPIService.calculate_line_kpis(line.id, day)

            snapshots.append(
                KPISnapshot(
                    factory_id=factory.id,
                    line_id=line.id,
                    machine=None,
                    operator=None,
                    shift=None,
                    snapshot_date=day,
                    total_production=result.total_production,
                    target_production=result.target_production,
                    efficiency_percent=result.efficiency_percent,
                    downtime_minutes=result.downtime_minutes,
                    uptime_minutes=1440 - result.downtime_minutes,
                    defect_count=0,
                    cycle_time_avg_seconds=result.cycle_time_avg_seconds,
                )
            )

        KPISnapshot.objects.filter(factory_id=factory.id, snapshot_date=day).delete()
        KPISnapshot.objects.bulk_create(snapshots, batch_size=500)

        return len(snapshots)

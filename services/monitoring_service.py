from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Avg, Exists, IntegerField, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.analytics.models import KPISnapshot
from apps.core.models import Line
from apps.devices.models import Event
from apps.monitoring.models import DowntimeLog

REALTIME_WINDOW_MINUTES = 2
PRODUCTION_EVENT_TYPE = "production_cycle"


def get_realtime_dashboard(factory_id) -> dict[str, Any]:
    now = timezone.now()
    window_start = now - timedelta(minutes=REALTIME_WINDOW_MINUTES)

    today = now.date()

    # Latest production event timestamp within window, per line
    last_production_at_sq = (
        Event.objects.filter(
            factory_id=factory_id,
            event_type=PRODUCTION_EVENT_TYPE,
            timestamp__gte=window_start,
            device__machine__line_id=OuterRef("pk"),
        )
        .order_by("-timestamp")
        .values("timestamp")[:1]
    )

    # Any active downtime on ANY machine in the line
    has_active_downtime_sq = DowntimeLog.objects.filter(
        factory_id=factory_id,
        ended_at__isnull=True,
        machine__line_id=OuterRef("pk"),
    )

    # KPI snapshots for today at line level (machine/operator null usually)
    today_kpi_sq = (
        KPISnapshot.objects.filter(
            factory_id=factory_id,
            line_id=OuterRef("pk"),
            snapshot_date=today,
        )
        .order_by()
        .values("total_production")[:1]
    )

    today_downtime_sq = (
        KPISnapshot.objects.filter(
            factory_id=factory_id,
            line_id=OuterRef("pk"),
            snapshot_date=today,
        )
        .order_by()
        .values("downtime_minutes")[:1]
    )

    lines_qs = (
        Line.objects.filter(factory_id=factory_id, is_active=True)
        .only("id", "name", "code")  # keep it light
        .annotate(
            has_active_downtime=Exists(has_active_downtime_sq),
            last_production_at=Subquery(last_production_at_sq),
            today_production=Coalesce(Subquery(today_kpi_sq), 0, output_field=IntegerField()),
            today_downtime_minutes=Coalesce(
                Subquery(today_downtime_sq), 0, output_field=IntegerField()
            ),
        )
        .order_by("name")
    )
    lines = []
    for line in lines_qs:
        if line.has_active_downtime:
            status = "DOWN"
        elif line.last_production_at is not None:
            status = "RUNNING"
        else:
            status = "IDLE"

    lines.append(
        {
            "id": str(line.id),
            "name": line.name,
            "code": line.code,
            "status": status,
            "last_event_at": (
                line.last_production_at.isoformat() if line.last_production_at else None
            ),
            "metrics": {
                "today_production": int(line.today_production or 0),
                "today_downtime_minutes": int(line.today_downtime_minutes or 0),
            },
        }
    )

    return {
        "factory_id": str(factory_id),
        "generated_at": now.isoformat(),
        "window_minutes": REALTIME_WINDOW_MINUTES,
        "lines": lines,
    }


def get_line_summary(factory_id, line_id, start_date, end_date):
    """
    Returns KPI-based summary for a line within [start_date, end_date].
    Uses daily KPI snapshots (fast, avoids scanning raw events).
    """

    line = (
        Line.objects.filter(id=line_id, factory_id=factory_id, is_active=True)
        .only("id", "name", "code")
        .first()
    )
    if not line:
        return None  # view will turn into 404 (tenant-safe)

    qs = (
        KPISnapshot.objects.filter(
            factory_id=factory_id,
            line_id=line_id,
            snapshot_date__gte=start_date,
            snapshot_date__lte=end_date,
        )
        .only("snapshot_date", "total_production", "downtime_minutes")  # keep light
        .order_by("snapshot_date")
    )

    agg = qs.aggregate(
        production_total=Sum("total_production"),
        downtime_minutes_total=Sum("downtime_minutes"),
        efficiency_avg=Avg("efficiency_percent"),
    )

    daily_points = [
        {
            "date": str(row.snapshot_date),
            "production": row.total_production or 0,
            "downtime_minutes": row.downtime_minutes or 0,
            "efficiency_percent": getattr(row, "efficiency_percent", None),
        }
        for row in qs
    ]

    return {
        "line": {"id": str(line.id), "name": line.name, "code": line.code},
        "date_range": {"start": str(start_date), "end": str(end_date)},
        "production_total": agg["production_total"] or 0,
        "downtime_minutes_total": agg["downtime_minutes_total"] or 0,
        "efficiency_avg": agg.get("efficiency_avg"),
        "daily_points": daily_points,
    }

# tasks/kpi_tasks.py
from __future__ import annotations

import logging
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from celery import shared_task
from django.core.mail import mail_admins
from django.utils import timezone

from apps.core.models import Factory
from services.kpi_service import KPIService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_daily_kpi_snapshots(self) -> dict:
    """
    Generate KPI snapshots for all factories.

    Intended behavior: run around 00:30 in each factory's local timezone.
    Practical approach: Beat triggers this periodically, and we decide
    which factories are "due" based on their local time.
    """
    now_utc = timezone.now()
    processed: int = 0
    skipped: int = 0
    failed: int = 0

    factories = Factory.objects.filter(is_active=True).only("id", "timezone")

    for factory in factories:
        try:
            factory_tz = ZoneInfo(factory.timezone)
            local_now = now_utc.astimezone(factory_tz)

            if not (local_now.hour == 0 and 25 <= local_now.minute <= 35):
                skipped += 1
                continue

            snapshot_date: date = local_now.date() - timedelta(days=1)

            KPIService.generate_kpi_snapshots(factory_id=factory.id, day=snapshot_date)
            processed += 1

        except Exception as exc:
            failed += 1
            logger.exception("KPI snapshot generation failed for factory=%s", factory.id)

            # Optional notification: send to ADMINS if configured
            try:
                mail_admins(
                    subject="KPI snapshot generation failed",
                    message=f"Factory: {factory.id}\nError: {exc}",
                    fail_silently=True,
                )
            except Exception:
                logger.exception("Failed to notify admins about KPI failure")

            raise self.retry(exc=exc)

    return {"processed": processed, "skipped": skipped, "failed": failed}

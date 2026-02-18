from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import TestCase

from apps.core.models import Factory
from tasks.kpi_tasks import generate_daily_kpi_snapshots


class TestGenerateDailyKPISnapshots(TestCase):
    @patch("tasks.kpi_tasks.KPIService.generate_kpi_snapshots")
    def test_runs_for_factories_in_0030_window(self, mock_generate):
        Factory.objects.create(
            name="F1",
            code="F1",
            timezone="Asia/Dhaka",
            is_active=True,
        )

        tz = ZoneInfo("Asia/Dhaka")
        local = datetime(2026, 2, 12, 0, 30, 0, tzinfo=tz)
        now_utc = local.astimezone(ZoneInfo("UTC"))

        with patch("tasks.kpi_tasks.timezone.now", return_value=now_utc):
            result = generate_daily_kpi_snapshots.apply().get()

        self.assertEqual(result["processed"], 1)
        mock_generate.assert_called_once()

    @patch("tasks.kpi_tasks.KPIService.generate_kpi_snapshots")
    def test_skips_when_not_in_window(self, mock_generate):
        Factory.objects.create(
            name="F1",
            code="F1",
            timezone="Asia/Dhaka",
            is_active=True,
        )

        tz = ZoneInfo("Asia/Dhaka")
        local = datetime(2026, 2, 12, 10, 0, 0, tzinfo=tz)
        now_utc = local.astimezone(ZoneInfo("UTC"))

        with patch("tasks.kpi_tasks.timezone.now", return_value=now_utc):
            result = generate_daily_kpi_snapshots.apply().get()

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["skipped"], 1)
        mock_generate.assert_not_called()

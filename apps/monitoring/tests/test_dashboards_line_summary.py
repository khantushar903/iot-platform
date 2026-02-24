from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.analytics.models import KPISnapshot
from apps.core.models import Factory, Line

TEST_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(CACHES=TEST_CACHE)
class LineSummaryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = Factory.objects.create(name="Factory A", code="FA")
        self.other_factory = Factory.objects.create(name="Factory B", code="FB")

        self.user = get_user_model().objects.create_user(username="u_sum", password="pass1234")
        profile = self.user.userprofile
        profile.factory = self.factory
        profile.role = "admin"
        profile.save()

        self.line = Line.objects.create(
            factory=self.factory, name="Line A", code="LA", is_active=True
        )
        self.other_line = Line.objects.create(
            factory=self.other_factory, name="Line B", code="LB", is_active=True
        )

        self.client.force_authenticate(user=self.user)

    def test_tenant_isolation_line_not_accessible(self):
        r = self.client.get(
            f"/api/v1/dashboards/line/{self.other_line.id}/summary/?start=2026-02-01&end=2026-02-02"
        )
        self.assertEqual(r.status_code, 404)

    def test_summary_aggregates_kpisnapshots(self):
        KPISnapshot.objects.create(
            factory=self.factory,
            line=self.line,
            snapshot_date=date(2026, 2, 1),
            total_production=10,
            downtime_minutes=5,
        )
        KPISnapshot.objects.create(
            factory=self.factory,
            line=self.line,
            snapshot_date=date(2026, 2, 2),
            total_production=20,
            downtime_minutes=7,
        )

        r = self.client.get(
            f"/api/v1/dashboards/line/{self.line.id}/summary/?start=2026-02-01&end=2026-02-02"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["production_total"], 30)
        self.assertEqual(r.data["downtime_minutes_total"], 12)
        self.assertEqual(len(r.data["daily_points"]), 2)

    @patch("apps.monitoring.views.get_line_summary")
    def test_summary_uses_cache(self, mock_service):
        cache.clear()
        mock_service.return_value = {
            "line": {"id": str(self.line.id), "name": "Line A", "code": "LA"},
            "date_range": {"start": "2026-02-01", "end": "2026-02-02"},
            "production_total": 0,
            "downtime_minutes_total": 0,
            "efficiency_avg": None,
            "daily_points": [],
        }

        url = f"/api/v1/dashboards/line/{self.line.id}/summary/?start=2026-02-01&end=2026-02-02"
        r1 = self.client.get(url)
        r2 = self.client.get(url)

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(mock_service.call_count, 1)

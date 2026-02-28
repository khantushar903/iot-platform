from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from apps.core.models import Factory, Line, Machine
from apps.devices.models import Device, Event
from apps.monitoring.models import DowntimeLog, DowntimeReason

TEST_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


def _without_profiling_middleware(middleware_list):
    """
    Remove Silk + Debug Toolbar middleware so assertNumQueries measures your code,
    not profiling/instrumentation queries.
    """
    blocked = (
        "silk.middleware.SilkyMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    return [m for m in middleware_list if m not in blocked]


@override_settings(CACHES=TEST_CACHE)
class RealtimeDashboardCacheTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.factory = Factory.objects.create(name="Factory A", code="FA")
        self.user = get_user_model().objects.create_user(username="u1", password="pass1234")

        profile = self.user.userprofile  # auto-created by signal
        profile.factory = self.factory
        profile.role = "admin"
        profile.save()

        self.client.force_authenticate(user=self.user)

    @patch("apps.monitoring.views.get_realtime_dashboard")
    def test_realtime_dashboard_uses_cache(self, mock_service):
        cache.clear()

        mock_service.return_value = {
            "factory_id": str(self.factory.id),
            "generated_at": "2026-02-22T00:00:00Z",
            "window_minutes": 2,
            "lines": [],
        }

        r1 = self.client.get("/api/v1/dashboards/realtime/")
        r2 = self.client.get("/api/v1/dashboards/realtime/")

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(mock_service.call_count, 1)


@override_settings(CACHES=TEST_CACHE)
class RealtimeDashboardTenantIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.factory_a = Factory.objects.create(name="Factory A", code="FA")
        self.factory_b = Factory.objects.create(name="Factory B", code="FB")

        self.user_a = get_user_model().objects.create_user(username="user_a", password="pass1234")
        profile = self.user_a.userprofile
        profile.factory = self.factory_a
        profile.role = "admin"
        profile.save()

        self.line_a = Line.objects.create(
            factory=self.factory_a, name="Line A", code="LA", is_active=True
        )
        self.line_b = Line.objects.create(
            factory=self.factory_b, name="Line B", code="LB", is_active=True
        )

        self.client.force_authenticate(user=self.user_a)

    def test_realtime_dashboard_returns_only_user_factory_lines(self):
        r = self.client.get("/api/v1/dashboards/realtime/")
        self.assertEqual(r.status_code, 200)

        line_ids = {item["id"] for item in r.data["lines"]}
        self.assertIn(str(self.line_a.id), line_ids)
        self.assertNotIn(str(self.line_b.id), line_ids)


@override_settings(CACHES=TEST_CACHE)
class RealtimeDashboardStatusPrecedenceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.factory = Factory.objects.create(name="Factory X", code="FX")
        self.line = Line.objects.create(
            factory=self.factory, name="Line X", code="LX", is_active=True
        )

        self.machine = Machine.objects.create(
            line=self.line,
            name="Machine X",
            code="MX",
            machine_type="GENERIC",
            is_active=True,
        )

        self.device = Device.objects.create(
            factory=self.factory,
            machine=self.machine,
            device_id="DEV-001",
            device_type="PLC",
            is_active=True,
        )

        self.user = get_user_model().objects.create_user(username="user_x", password="pass1234")
        profile = self.user.userprofile
        profile.factory = self.factory
        profile.role = "admin"
        profile.save()

        self.client.force_authenticate(user=self.user)

    def test_down_status_overrides_running(self):
        # Recent production event (within realtime window)
        Event.objects.create(
            factory=self.factory,
            device=self.device,
            event_type="production_cycle",
            timestamp=timezone.now(),
            payload={"output_count": 1},
        )

        reason = DowntimeReason.objects.create(
            factory=self.factory,
            code="TEST",
            description="Test Reason",
            category="Mechanical",
            is_active=True,
        )

        DowntimeLog.objects.create(
            factory=self.factory,
            machine=self.machine,
            reason=reason,
            started_at=timezone.now() - timedelta(minutes=1),
            ended_at=None,
        )

        r = self.client.get("/api/v1/dashboards/realtime/")
        self.assertEqual(r.status_code, 200)

        line_data = r.data["lines"][0]
        self.assertEqual(line_data["status"], "DOWN")


@override_settings(CACHES=TEST_CACHE)
class RealtimeDashboardMultipleLinesTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.factory = Factory.objects.create(name="Factory M", code="FM")

        self.user = get_user_model().objects.create_user(
            username="user_multi_line", password="pass1234"
        )
        profile = self.user.userprofile
        profile.factory = self.factory
        profile.role = "admin"
        profile.save()

        self.line_1 = Line.objects.create(
            factory=self.factory, name="Line 1", code="L1", is_active=True
        )
        self.line_2 = Line.objects.create(
            factory=self.factory, name="Line 2", code="L2", is_active=True
        )

        self.client.force_authenticate(user=self.user)

    def test_realtime_dashboard_returns_all_lines_in_factory(self):
        r = self.client.get("/api/v1/dashboards/realtime/")
        self.assertEqual(r.status_code, 200)

        line_ids = {item["id"] for item in r.data["lines"]}
        self.assertIn(str(self.line_1.id), line_ids)
        self.assertIn(str(self.line_2.id), line_ids)
        self.assertGreaterEqual(len(r.data["lines"]), 2)

    @override_settings(MIDDLEWARE=_without_profiling_middleware(settings.MIDDLEWARE))
    def test_realtime_dashboard_query_count_under_limit(self):
        cache.clear()  # ensure no cache hit

        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get("/api/v1/dashboards/realtime/")
            self.assertEqual(r.status_code, 200)

        self.assertLessEqual(len(ctx), 3)

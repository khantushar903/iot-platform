from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.core.models import Factory, Line, Machine
from apps.devices.models import Device, Event

TEST_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(CACHES=TEST_CACHE)
class RealtimeCacheInvalidationTests(TestCase):
    def setUp(self):
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

    def test_production_event_invalidates_realtime_cache_key(self):
        key = f"dash:realtime:factory:{self.factory.id}"
        cache.set(key, {"cached": True}, timeout=60)
        self.assertIsNotNone(cache.get(key))

        Event.objects.create(
            factory=self.factory,
            device=self.device,
            event_type="production_cycle",
            timestamp=timezone.now(),
            payload={"output_count": 1},
        )

        self.assertIsNone(cache.get(key))

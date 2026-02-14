from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Factory, Line, Machine
from apps.devices.models import Device, Event


class DeviceModelTests(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")
        self.line = Line.objects.create(
            factory=self.factory,
            name="Line 1",
            code="L1",
            capacity_per_hour=100,
        )
        self.machine = Machine.objects.create(
            line=self.line,
            name="Machine 1",
            code="M1",
            machine_type="Cutter",
        )

    def test_device_id_unique(self):
        Device.objects.create(
            factory=self.factory,
            device_id="DEV-1",
            device_type="ESP32",
        )

        with self.assertRaises(IntegrityError):
            Device.objects.create(
                factory=self.factory,
                device_id="DEV-1",
                device_type="ESP32",
            )

    def test_event_idempotency_key_unique(self):
        device = Device.objects.create(
            factory=self.factory,
            machine=self.machine,
            device_id="DEV-1",
            device_type="ESP32",
        )

        Event.objects.create(
            device=device,
            factory=self.factory,
            timestamp=timezone.now(),
            event_type="telemetry",
            payload={"temp": 22},
            idempotency_key="IDEMP-1",
        )

        with self.assertRaises(IntegrityError):
            Event.objects.create(
                device=device,
                factory=self.factory,
                timestamp=timezone.now(),
                event_type="telemetry",
                payload={"temp": 23},
                idempotency_key="IDEMP-1",
            )

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Factory, Line, Machine
from apps.monitoring.models import DowntimeLog, DowntimeReason, Shift


class MonitoringModelTests(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")
        self.line = Line.objects.create(
            factory=self.factory, name="Line 1", code="L1", capacity_per_hour=100
        )
        self.machine = Machine.objects.create(
            line=self.line, name="Machine 1", code="M1", machine_type="Cutter"
        )

    def test_shift_unique_per_factory_name(self):
        Shift.objects.create(
            factory=self.factory,
            name="A",
            start_time="08:00",
            end_time="16:00",
            is_active=True,
        )
        with self.assertRaises(IntegrityError):
            Shift.objects.create(
                factory=self.factory,
                name="A",
                start_time="09:00",
                end_time="17:00",
                is_active=True,
            )

    def test_downtime_reason_unique_per_factory_code(self):
        DowntimeReason.objects.create(
            factory=self.factory,
            code="MECH-1",
            description="Mechanical issue",
            category="Mechanical",
            is_active=True,
        )
        with self.assertRaises(IntegrityError):
            DowntimeReason.objects.create(
                factory=self.factory,
                code="MECH-1",
                description="Duplicate",
                category="Mechanical",
                is_active=True,
            )

    def test_downtime_log_create(self):
        reason = DowntimeReason.objects.create(
            factory=self.factory,
            code="MAT-1",
            description="Material shortage",
            category="Material",
            is_active=True,
        )
        log = DowntimeLog.objects.create(
            machine=self.machine,
            factory=self.factory,
            reason=reason,
            started_at=timezone.now(),
            ended_at=None,
            duration_minutes=None,
            notes="",
        )
        self.assertEqual(log.factory_id, self.factory.id)
        self.assertEqual(log.machine_id, self.machine.id)

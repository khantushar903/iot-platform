from django.db import IntegrityError
from django.test import TestCase

from apps.analytics.models import KPISnapshot
from apps.core.models import Factory, Line, Machine, Operator
from apps.monitoring.models import Shift


class AnalyticsModelTests(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")
        self.line = Line.objects.create(
            factory=self.factory, name="Line 1", code="L1", capacity_per_hour=100
        )
        self.machine = Machine.objects.create(
            line=self.line, name="Machine 1", code="M1", machine_type="Cutter"
        )
        self.operator = Operator.objects.create(
            factory=self.factory, employee_id="E1", name="Op 1", skill_level=2
        )
        self.shift = Shift.objects.create(
            factory=self.factory,
            name="A",
            start_time="08:00",
            end_time="16:00",
            is_active=True,
        )

    def test_kpisnapshot_unique_together(self):
        KPISnapshot.objects.create(
            factory=self.factory,
            line=self.line,
            machine=self.machine,
            operator=self.operator,
            snapshot_date="2026-02-04",
            shift=self.shift,
            total_production=10,
            target_production=20,
            uptime_minutes=100,
            downtime_minutes=20,
            defect_count=1,
        )

        with self.assertRaises(IntegrityError):
            KPISnapshot.objects.create(
                factory=self.factory,
                line=self.line,
                machine=self.machine,
                operator=self.operator,
                snapshot_date="2026-02-04",
                shift=self.shift,
                total_production=11,
                target_production=21,
                uptime_minutes=101,
                downtime_minutes=21,
                defect_count=0,
            )

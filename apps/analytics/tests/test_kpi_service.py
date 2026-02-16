from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.analytics.models import KPISnapshot
from apps.core.models import Factory, Line, Machine
from apps.devices.models import Device, Event
from apps.monitoring.models import DowntimeLog
from services.kpi_service import KPIService


class KPIServiceTests(TestCase):

    def setUp(self):
        self.factory = Factory.objects.create(
            name="Test Factory",
            code="F1",
            timezone="Asia/Dhaka",
        )

        self.line = Line.objects.create(
            factory=self.factory,
            name="Line 1",
            code="L1",
            is_active=True,
            capacity_per_hour=10,  # target = 240
        )

        self.machine = Machine.objects.create(
            line=self.line,
            name="M1",
            code="M1",
            machine_type="press",
        )

        self.device = Device.objects.create(
            factory=self.factory,
            machine=self.machine,
            device_id="dev-1",
            device_type="sensor",
        )

        self.day = date(2026, 2, 16)
        self.ts = timezone.make_aware(datetime(2026, 2, 16, 3, 0, 0), timezone=timezone.utc)

    def _create_production(self, count):
        Event.objects.create(
            factory=self.factory,
            device=self.device,
            event_type="production_cycle",
            timestamp=self.ts,
            payload={"output_count": count},
        )

    def _generate_snapshot(self):
        KPIService.generate_kpi_snapshots(self.factory.id, self.day)
        return KPISnapshot.objects.get(factory=self.factory, line=self.line)

    # 1️⃣ total production
    def test_total_production_calculation(self):
        self._create_production(3)
        snap = self._generate_snapshot()
        self.assertEqual(snap.total_production, 3)

    # 2️⃣ target production
    def test_target_production_calculation(self):
        snap = self._generate_snapshot()
        self.assertEqual(snap.target_production, 240)

    # 3️⃣ efficiency calculation
    def test_efficiency_calculation(self):
        self._create_production(12)
        snap = self._generate_snapshot()
        # (12 / 240) * 100 = 5%
        self.assertEqual(snap.efficiency_percent, Decimal("5.00"))

    # 4️⃣ downtime calculation
    def test_downtime_calculation(self):
        DowntimeLog.objects.create(
            factory=self.factory,
            machine=self.machine,
            started_at=self.ts,
            duration_minutes=30,
        )
        snap = self._generate_snapshot()
        self.assertEqual(snap.downtime_minutes, 30)

    # 5️⃣ uptime calculation
    def test_uptime_calculation(self):
        DowntimeLog.objects.create(
            factory=self.factory,
            machine=self.machine,
            started_at=self.ts,
            duration_minutes=60,
        )
        snap = self._generate_snapshot()
        self.assertEqual(snap.uptime_minutes, 1440 - 60)

    # 6️⃣ defect default
    def test_defect_default_zero(self):
        snap = self._generate_snapshot()
        self.assertEqual(snap.defect_count, 0)

    # 7️⃣ snapshot structure (line-level daily)
    def test_snapshot_structure_line_level(self):
        snap = self._generate_snapshot()
        self.assertIsNotNone(snap.line_id)
        self.assertIsNone(snap.machine_id)
        self.assertIsNone(snap.operator_id)
        self.assertIsNone(snap.shift_id)

    # 8️⃣ idempotency
    def test_snapshot_idempotent(self):
        KPIService.generate_kpi_snapshots(self.factory.id, self.day)
        KPIService.generate_kpi_snapshots(self.factory.id, self.day)
        count = KPISnapshot.objects.filter(factory=self.factory, line=self.line).count()
        self.assertEqual(count, 1)

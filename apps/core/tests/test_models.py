from django.db import IntegrityError
from django.test import TestCase

from apps.core.models import Factory, Line, Machine, Operator


class CoreModelTests(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")

    def test_line_unique_per_factory_code(self):
        Line.objects.create(
            factory=self.factory,
            name="Line 1",
            code="L1",
            capacity_per_hour=100,
        )

        with self.assertRaises(IntegrityError):
            Line.objects.create(
                factory=self.factory,
                name="Line 2",
                code="L1",
                capacity_per_hour=120,
            )

    def test_machine_unique_per_line_code(self):
        line = Line.objects.create(
            factory=self.factory,
            name="Line 1",
            code="L1",
            capacity_per_hour=100,
        )

        Machine.objects.create(
            line=line,
            name="Machine 1",
            code="M1",
            machine_type="Cutter",
        )

        with self.assertRaises(IntegrityError):
            Machine.objects.create(
                line=line,
                name="Machine 2",
                code="M1",
                machine_type="Cutter",
            )

    def test_operator_employee_id_unique(self):
        Operator.objects.create(
            factory=self.factory,
            employee_id="E1",
            name="Operator 1",
            skill_level=1,
        )

        with self.assertRaises(IntegrityError):
            Operator.objects.create(
                factory=self.factory,
                employee_id="E1",
                name="Operator 2",
                skill_level=2,
            )

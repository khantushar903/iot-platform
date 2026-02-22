from django.db import IntegrityError
from django.test import TestCase

from apps.alerts.models import Alert, AlertRule
from apps.core.models import Factory


class AlertsModelTests(TestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")

    def test_alertrule_unique_per_factory_name(self):
        AlertRule.objects.create(
            factory=self.factory,
            name="High Downtime",
            metric_name="downtime_minutes",
            condition="gt",
            threshold_value="30.00",
            severity="warning",
            is_active=True,
        )
        with self.assertRaises(IntegrityError):
            AlertRule.objects.create(
                factory=self.factory,
                name="High Downtime",
                metric_name="downtime_minutes",
                condition="gt",
                threshold_value="40.00",
                severity="critical",
                is_active=True,
            )

    def test_alert_create(self):
        rule = AlertRule.objects.create(
            factory=self.factory,
            name="High Downtime",
            metric_name="downtime_minutes",
            condition="gt",
            threshold_value="30.00",
            severity="warning",
            is_active=True,
        )
        alert = Alert.objects.create(
            factory=self.factory,
            rule=rule,
            status="open",
            message="Downtime exceeded threshold",
        )
        self.assertEqual(alert.status, "open")

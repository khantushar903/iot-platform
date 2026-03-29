from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserProfile
from apps.core.models import Factory
from apps.devices.models import Device, Event

User = get_user_model()


class EventIngestionAPITests(APITestCase):
    def setUp(self):
        # Create a factory + device for tests
        self.factory = Factory.objects.create(name="Factory 1", code="F1")

        self.device = Device.objects.create(
            factory=self.factory,
            machine=None,
            device_id="DEV-001",
            device_type="sensor",
            is_active=True,
            metadata={},
            last_seen_at=timezone.now(),  # if your model requires it
        )

        # Create user + JWT token
        self.user = User.objects.create_user(username="u1", password="pass12345")

        UserProfile.objects.filter(user=self.user).update(
            factory=self.factory,
            role="manager",
        )

        token = RefreshToken.for_user(self.user)
        self.access_token = str(token.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # /api/v1/events/ is mapped to name="event-create" from your urls.py
        self.url = reverse("event-create")

    def test_post_event_success(self):
        idem = str(uuid.uuid4())

        payload = {
            "device_id": "DEV-001",
            "timestamp": timezone.now().isoformat(),
            "event_type": "production_cycle",
            "payload": {"output_count": 1},
        }

        res = self.client.post(self.url, payload, format="json", HTTP_IDEMPOTENCY_KEY=idem)
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["status"], "processed")
        self.assertEqual(Event.objects.count(), 1)

    def test_post_event_idempotency_duplicate(self):
        idem = str(uuid.uuid4())

        payload = {
            "device_id": "DEV-001",
            "timestamp": timezone.now().isoformat(),
            "event_type": "production_cycle",
            "payload": {"output_count": 1},
        }

        res1 = self.client.post(self.url, payload, format="json", HTTP_IDEMPOTENCY_KEY=idem)
        self.assertEqual(res1.status_code, 201)
        created_id = res1.data["id"]

        res2 = self.client.post(self.url, payload, format="json", HTTP_IDEMPOTENCY_KEY=idem)
        self.assertEqual(res2.status_code, 409)
        self.assertEqual(res2.data["error"], "duplicate")
        self.assertEqual(res2.data["existing_id"], created_id)

        self.assertEqual(Event.objects.count(), 1)

    def test_get_events_returns_results(self):
        Event.objects.create(
            device=self.device,
            factory=self.factory,
            timestamp=timezone.now(),
            event_type="production_cycle",
            payload={"output_count": 1},
            idempotency_key="k1",
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)
        self.assertEqual(len(res.data["results"]), 1)

    def test_get_events_filter_by_device_and_type(self):
        Event.objects.create(
            device=self.device,
            factory=self.factory,
            timestamp=timezone.now(),
            event_type="production_cycle",
            payload={"output_count": 1},
            idempotency_key="k1",
        )
        Event.objects.create(
            device=self.device,
            factory=self.factory,
            timestamp=timezone.now(),
            event_type="downtime_start",
            payload={"reason": "maintenance"},
            idempotency_key="k2",
        )

        res = self.client.get(self.url, {"device_id": "DEV-001", "event_type": "production_cycle"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["event_type"], "production_cycle")
        self.assertEqual(res.data["results"][0]["device_id"], "DEV-001")

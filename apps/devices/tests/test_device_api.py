from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Factory
from apps.devices.models import Device

User = get_user_model()


class DeviceAPITests(APITestCase):
    def setUp(self):
        self.factory = Factory.objects.create(name="Factory 1", code="F1")

        self.device = Device.objects.create(
            factory=self.factory,
            machine=None,
            device_id="DEV-001",
            device_type="sensor",
            last_seen_at=timezone.now(),
            is_active=True,
            metadata={},
        )

        self.user = User.objects.create_user(username="u1", password="pass12345")
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        self.list_url = reverse("device-list-create")
        self.detail_url = reverse("device-detail", kwargs={"pk": self.device.pk})

    def test_list_devices(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, 200)
        # DRF may paginate if configured; handle both cases
        if isinstance(res.data, dict) and "results" in res.data:
            results = res.data["results"]
        else:
            results = res.data
        self.assertTrue(any(d["device_id"] == "DEV-001" for d in results))

    def test_create_device(self):
        payload = {
            "factory": str(self.factory.id),
            "machine": None,
            "device_id": "DEV-002",
            "device_type": "sensor",
            "last_seen_at": timezone.now().isoformat(),
            "is_active": True,
            "metadata": {},
        }
        res = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(Device.objects.filter(device_id="DEV-002").exists())

    def test_update_device(self):
        payload = {"device_type": "camera"}
        res = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.device.refresh_from_db()
        self.assertEqual(self.device.device_type, "camera")

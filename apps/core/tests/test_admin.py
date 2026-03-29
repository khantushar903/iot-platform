from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Factory, Line


class CoreAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            password="pass12345",
            email="admin@test.com",
        )
        self.client.login(username="admin_test", password="pass12345")

    def _factory_payload(self):
        """
        Build a payload that satisfies required (blank=False, null=False) fields
        for the Factory admin add form, without guessing your exact schema.
        """
        payload = {}

        for field in Factory._meta.fields:
            # Skip PK/ID fields
            if field.primary_key or isinstance(field, (models.AutoField, models.BigAutoField)):
                continue

            # Skip auto timestamp fields if present
            if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
                continue

            # Only fill required fields
            if field.blank or field.null:
                continue

            # Provide defaults by field type/name
            if isinstance(field, models.CharField):
                if field.name == "code":
                    payload[field.name] = "TF-001"
                elif field.name == "name":
                    payload[field.name] = "Test Factory"
                else:
                    payload[field.name] = "x"
            elif isinstance(field, models.BooleanField):
                payload[field.name] = True
            elif isinstance(field, models.IntegerField):
                payload[field.name] = 1
            elif isinstance(field, models.DateField):
                payload[field.name] = "2026-02-14"
            elif isinstance(field, models.DateTimeField):
                payload[field.name] = "2026-02-14 00:00:00"
            else:
                # Fallback for any other required field types
                payload[field.name] = "x"

        return payload

    def test_admin_can_create_factory(self):
        url = reverse("admin:core_factory_add")
        payload = self._factory_payload()

        res = self.client.post(url, payload)

        # If validation fails, admin returns 200 with form errors.
        # Print them so you can quickly see what's missing.
        if res.status_code == 200 and "adminform" in res.context:
            print("ADMIN FORM ERRORS:", res.context["adminform"].form.errors)

        self.assertEqual(res.status_code, 302)  # redirect after success
        self.assertTrue(Factory.objects.filter(code=payload.get("code", "TF-001")).exists())

    def test_admin_can_filter_lines_by_factory(self):
        f1 = Factory.objects.create(name="F1", code="F1", is_active=True)
        f2 = Factory.objects.create(name="F2", code="F2", is_active=True)

        Line.objects.create(factory=f1, name="L1", code="L1", capacity_per_hour=10, is_active=True)
        Line.objects.create(factory=f2, name="L2", code="L2", capacity_per_hour=10, is_active=True)

        url = reverse("admin:core_line_changelist")
        res = self.client.get(url, {"factory__id__exact": str(f1.id)})

        self.assertEqual(res.status_code, 200)
        qs = res.context["cl"].queryset
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "L1")

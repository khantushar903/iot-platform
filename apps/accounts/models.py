from django.contrib.auth.models import User
from django.db import models

from apps.core.models import Factory


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, null=True)

    role = models.CharField(
        max_length=50,
        choices=[
            ("admin", "Admin"),
            ("manager", "Manager"),
            ("supervisor", "Supervisor"),
            ("viewer", "Viewer"),
        ],
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

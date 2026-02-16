import os

from celery import Celery

# Default Django settings module for 'celery' command-line programs.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("iot_platform")

# Read config from Django settings, using CELERY_ prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps.
app.autodiscover_tasks()

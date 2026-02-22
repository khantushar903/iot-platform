import os

from celery import Celery
from celery.schedules import crontab

# Default Django settings module for 'celery' command-line programs.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("iot_platform")

# Read config from Django settings, using CELERY_ prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps.
app.autodiscover_tasks()
app.conf.imports = ("tasks.kpi_tasks", "tasks.ingestion_tasks")

app.conf.beat_schedule = {
    "generate_daily_kpi_snapshots_every_5_min": {
        "task": "tasks.kpi_tasks.generate_daily_kpi_snapshots",
        "schedule": crontab(minute="*/5"),
    },
}

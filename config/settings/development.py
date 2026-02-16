# flake8: noqa
from .base import *

DEBUG = True

# Celery dev mode: run tasks instantly (no Redis/Docker required)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

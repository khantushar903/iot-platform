# Celery Setup Documentation

## Overview

Celery is used for background task processing in the IoT Platform.

Instead of executing heavy logic inside API request-response cycles, tasks are sent to a queue and processed asynchronously by workers.

This improves performance, scalability, and reliability.

---

## Architecture

Client → Django API → Redis (Broker) → Celery Worker → Database

- Django handles incoming requests.
- Celery sends tasks to Redis.
- Worker consumes tasks from Redis and executes them.

---

## Configuration

### Celery App Initialization

File: `config/celery.py`

- Creates Celery application instance.
- Loads configuration from Django settings.
- Auto-discovers tasks from `tasks/` package.

---

### Broker Configuration

In `config/settings/base.py`:

```python
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Dhaka"
```

Redis is used as:

- Message broker
- Result backend

---

## Development Mode (Low Resource Setup)

In `config/settings/development.py`:

```python
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

This makes Celery tasks execute immediately without Redis or Docker.

Used for:

- Local development
- Unit testing
- Low-RAM environments

---

## Running Celery Worker (Real Async Mode)

1. Start Redis:

```bash
docker start redis
```

2. Start Celery worker:

```bash
celery -A config worker -l info -P solo
```

Note:

- `-P solo` is required on Windows.

---

## Retry Policy

Example task:

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=5)
```

- Retries up to 3 times.
- Waits 5 seconds between retries.
- Improves fault tolerance.

---

## Why Celery?

- Keeps API response times low.
- Enables background processing.
- Provides retry and failure handling.
- Supports scalable architecture.

```

---

```

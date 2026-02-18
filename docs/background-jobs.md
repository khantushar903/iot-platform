# Background Jobs Strategy

## Purpose

Background jobs are used to process heavy or time-consuming logic outside API request-response cycles.

This ensures:

- Fast API performance
- Improved scalability
- Better reliability
- Reduced API latency for analytics-heavy endpoints

---

## Current Background Tasks

---

### Event Processing (Ingestion)

File: `tasks/ingestion_tasks.py`

Trigger:

- Called using `.delay()` after an Event is created.

Purpose:

- Handle post-ingestion logic.
- Prepare for KPI calculations.
- Future support for alert evaluation.

Flow:

1. API creates Event record.
2. `.delay()` enqueues task.
3. Redis stores task message.
4. Celery Worker executes task.

---

### Daily KPI Snapshot Generation

File: `tasks/kpi_tasks.py`

Task Name:
`generate_daily_kpi_snapshots`

Schedule:
Runs every **5 minutes** via Celery Beat.

```python
"generate_daily_kpi_snapshots_every_5_min": {
    "task": "tasks.kpi_tasks.generate_daily_kpi_snapshots",
    "schedule": crontab(minute="*/5"),
}
```

### Purpose:

Generate daily KPI snapshots for all active factories.

### Why this exists:

Instead of calculating KPIs every time a manager opens the dashboard,
we precompute them once per day and store results in `KPISnapshot`.

This improves:

- Dashboard performance
- Historical reporting reliability
- Database efficiency
- Multi-tenant scalability

---

### Execution Logic

1. Task runs every 5 minutes.
2. For each active factory:
   - Convert current UTC time to factory timezone using `ZoneInfo`.
   - If local time is between **00:25 – 00:35**, generate snapshot.

3. Snapshot date = yesterday (factory local date).
4. Existing snapshots for that date are deleted.
5. New snapshots are bulk created.

This design ensures:

- Timezone-aware multi-factory support
- Safe re-runs
- Idempotent behavior

---

## Retry Strategy

Tasks use:

```python
max_retries=3
default_retry_delay=60
```

This ensures:

- Temporary Redis/DB failures are retried.
- System remains resilient.
- Snapshot generation is not permanently skipped due to transient errors.

On failure:

- Errors are logged.
- `mail_admins()` is triggered if configured.

---

## Idempotency Strategy

KPI snapshot generation deletes existing records before bulk creating:

```python
KPISnapshot.objects.filter(...).delete()
KPISnapshot.objects.bulk_create(...)
```

This guarantees:

- No duplicate snapshots.
- Safe retry behavior.
- Consistent daily data.

---

## Development vs Production Mode

Development:

- Tasks may run in eager mode (execute immediately).
- Useful for unit testing.

Production:

- Tasks run through Redis.
- Celery Worker consumes tasks.
- Celery Beat schedules periodic tasks.

---

## How to Run Background Jobs Locally

Start Redis (Docker):

```
docker start redis
```

Start Celery Worker (low memory mode recommended):

```
celery -A config worker -l info -P solo --concurrency=1
```

Trigger manually (optional):

```
python manage.py shell
```

```python
from tasks.kpi_tasks import generate_daily_kpi_snapshots
generate_daily_kpi_snapshots.delay()
```

Optional: Start Beat (scheduler):

```
celery -A config beat -l info
```

---

## Architecture Principles Followed

- Business logic lives in `services/`
- Tasks are thin wrappers
- Timezone-aware scheduling
- Retry + failure handling
- Unit tests for scheduled logic
- Explicit task imports for project-level task modules

---

## Future Background Job Categories

Planned additions:

- Alert rule evaluation
- Automated reporting
- Data cleanup & maintenance jobs
- Periodic anomaly detection

Each will follow:

- Dedicated task file
- Retry policy
- Logging strategy
- Test coverage

---

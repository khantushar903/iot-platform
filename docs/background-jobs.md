# Background Jobs Strategy

## Purpose

Background jobs are used to process heavy or time-consuming logic outside API request-response cycles.

This ensures:

- Fast API performance
- Improved scalability
- Better reliability

---

## Current Background Tasks

### 1. Event Processing

File: `tasks/ingestion_tasks.py`

Triggered after an event is created.

Purpose:

- Handle post-ingestion logic.
- Prepare for KPI calculations and alert evaluations.

---

## Task Flow

1. API creates Event record.
2. `.delay()` enqueues task.
3. Redis stores task message.
4. Worker executes task.

---

## Retry Strategy

Tasks use:

```python
max_retries=3
default_retry_delay=5
```

This ensures:

- Temporary failures are retried.
- System remains resilient.

---

## Development Mode

Eager mode runs tasks immediately.

Production mode runs tasks through Redis + Worker.

---

## Future Task Categories

Planned categories:

- KPI snapshot generation
- Alert rule evaluation
- Report generation
- Data cleanup and maintenance

Each category will have:

- Dedicated task file
- Retry policy
- Monitoring metrics

---

## Best Practices

- Keep business logic in `services/`
- Keep tasks thin (call service methods)
- Always write tests
- Avoid heavy logic inside API views

```

---

```

# Service Layer Pattern

## Goal

Keep Django REST Framework views (controllers) thin and predictable.

**Rule**: Views must not contain business logic.  
All domain/business logic lives in `services/`.

## Why we use a service layer

- Easier to test business logic without HTTP requests
- Reusable logic across API endpoints, Celery tasks, management commands
- Views stay small and readable
- Prevents “fat views” and duplicated logic

## Pattern used in this project

### Thin View

The view only:

1. Validates request data via serializer
2. Reads headers (e.g., Idempotency-Key)
3. Calls the service method
4. Returns HTTP response

Example (events):

- Serializer validates device_id/timestamp/event_type
- View calls `IngestionService.create_event(...)`
- View returns:
  - `201 {"id": ..., "status": "processed"}`
  - `409 {"error": "duplicate", "existing_id": ...}`

### Service = Business Logic

The service:

- loads device + factory
- checks idempotency
- creates event
- returns `(event, created)` so caller can decide HTTP response

Files:

- `services/ingestion_service.py`

## What should NOT go in views

- database workflows (multiple related queries)
- validation that depends on database/business rules
- idempotency handling logic
- KPI calculations, alert evaluation, report generation

## What services may do

- enforce business rules
- orchestrate database writes
- return helpful results (like `(object, created)`)
- be used by Celery tasks later (Day 5+)

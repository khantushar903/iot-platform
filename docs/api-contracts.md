# API Contracts (v1)

Base URL Prefix: `/api/v1/`  
Authentication: JWT Bearer Token required for protected endpoints.

---

# 1. Authentication

## POST `/api/auth/login/`

Login and receive access + refresh tokens.

### Request

```json
{
  "username": "tushar",
  "password": "1234567890"
}
```

---

### Response

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

---

## POST `/api/auth/refresh/`

Generate a new access token using refresh token.

### Request

```json
{
  "refresh": "<refresh_token>"
}
```

### Response

```json
{
  "access": "<new_access_token>"
}
```

---

# 2. Event Ingestion API

## POST `/api/v1/events/`

Creates a new device event.

### Headers

- `Authorization: Bearer <access_token>`
- `Idempotency-Key: <uuid>` (recommended)

### Request Body

```json
{
  "device_id": "DEV-001",
  "timestamp": "2026-02-14T08:46:47.871Z",
  "event_type": "production_cycle",
  "payload": {
    "output_count": 1
  }
}
```

### Success Response (201)

```json
{
  "id": 123,
  "status": "processed"
}
```

### Duplicate Response (409)

```json
{
  "error": "duplicate",
  "existing_id": 123
}
```

### Validation Rules

- Device must exist and be active.
- Timestamp cannot be in the future.
- `event_type` must be one of:
  - `production_cycle`
  - `downtime_start`
  - `downtime_end`

---

## GET `/api/v1/events/`

Retrieve events with filtering and cursor pagination.

### Query Parameters (optional)

- `factory_id=<uuid>`
- `device_id=DEV-001`
- `event_type=production_cycle`
- `start=<ISO datetime>`
- `end=<ISO datetime>`
- `cursor=<pagination_token>`

### Example Request

```
GET /api/v1/events/?device_id=DEV-001&event_type=production_cycle
```

### Response

```json
{
  "next": "http://127.0.0.1:8000/api/v1/events/?cursor=abc123",
  "previous": null,
  "results": [
    {
      "id": 1,
      "device_id": "DEV-001",
      "timestamp": "2026-02-14T08:46:47.871Z",
      "event_type": "production_cycle",
      "payload": {
        "output_count": 1
      },
      "idempotency_key": "123e4567-e89b-12d3-a456-426614174000"
    }
  ]
}
```

---

# 3. Device Management API

## GET `/api/v1/devices/`

Returns a list of registered devices.

### Response

```json
[
  {
    "id": "uuid",
    "factory": "factory_uuid",
    "machine": null,
    "device_id": "DEV-001",
    "device_type": "sensor",
    "last_seen_at": "2026-02-14T08:46:47.871Z",
    "is_active": true,
    "metadata": {}
  }
]
```

---

## POST `/api/v1/devices/`

Creates a new device.

### Request Body

```json
{
  "factory": "<factory_uuid>",
  "machine": null,
  "device_id": "DEV-002",
  "device_type": "sensor",
  "last_seen_at": "2026-02-14T08:46:47.871Z",
  "is_active": true,
  "metadata": {}
}
```

### Success Response (201)

```json
{
  "id": "uuid",
  "factory": "<factory_uuid>",
  "machine": null,
  "device_id": "DEV-002",
  "device_type": "sensor",
  "last_seen_at": "2026-02-14T08:46:47.871Z",
  "is_active": true,
  "metadata": {}
}
```

---

## PATCH `/api/v1/devices/<uuid>/`

Partially update a device.

### Example Request

```json
{
  "device_type": "camera"
}
```

---

## DELETE `/api/v1/devices/<uuid>/`

Deletes a device.

### Success Response

HTTP 204 No Content

---

# Pagination Strategy

Event listing uses **CursorPagination**:

- Default page size: 50
- Ordered by `-timestamp`
- Response includes `next` and `previous` cursor URLs.

---

# Idempotency Strategy

- Clients should send an `Idempotency-Key` header when calling POST `/events/`.
- If the same key is reused, server returns:
  - `409 duplicate`
  - existing event ID

- Guarantees at-most-once event creation.

---

# Error Handling

Validation errors return HTTP 400 with field-specific messages.

Example:

```json
{
  "device_id": ["Device not found or inactive"],
  "timestamp": ["Future timestamps not allowed"]
}
```

Authentication failures return:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

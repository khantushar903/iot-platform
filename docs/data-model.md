# Data Model

## Overview
This project uses a tenant boundary model where `Factory` is the top-level owner for operational entities and time-series data.

## Core Entities
- **Factory**: Tenant boundary
- **Line**: Production line within a factory (unique per factory by `code`)
- **Machine**: Workstation within a line (unique per line by `code`)
- **Operator**: Factory operator (employee_id unique)

## Devices
- **Device**: IoT device installed in a factory (optionally attached to a machine)
- **Event**: Time-series telemetry/event data from devices

## Relationships (high level)
- Factory 1—* Line
- Line 1—* Machine
- Factory 1—* Operator
- Factory 1—* Device
- Device 1—* Event
- Factory 1—* Event

## ER Diagram
- Diagram tool: dbdiagram.io
- Diagram link: (add link here)
- Exported image: (optional)

## Constraints & Indexes (high value)
- Uniqueness:
  - Factory.code (unique)
  - Line(factory, code)
  - Machine(line, code)
  - Operator.employee_id (unique)
  - Device.device_id (unique)
  - Event.idempotency_key (unique, nullable)
- Indexes:
  - Factory(code, is_active)
  - Line(factory, is_active)
  - Machine(line, is_active)
  - Operator(factory, is_active), Operator(employee_id)
  - Device(factory, is_active), Device(device_id)
  - Event(factory, timestamp), (device, timestamp), (event_type, timestamp), (idempotency_key)

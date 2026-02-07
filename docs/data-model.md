# Data Model

## Overview

This project uses a tenant-based architecture where `Factory` is the top-level boundary.
All operational, time-series, analytics, and alerting data are scoped to a factory.

## Core Entities

- **Factory**: Tenant boundary
- **Line**: Production line within a factory (unique per factory by `code`)
- **Machine**: Workstation within a line (unique per line by `code`)
- **Operator**: Factory operator (`employee_id` unique)

## Devices

- **Device**: IoT device installed in a factory (optionally attached to a machine)
- **Event**: Time-series telemetry/event data emitted by devices

## Monitoring

- **Shift**: Shift configuration for a factory
- **DowntimeReason**: Categorized downtime reasons (unique per factory by `code`)
- **DowntimeLog**: Recorded downtime incidents for machines

## Analytics

- **KPISnapshot**: Pre-aggregated KPI values per day, scoped by factory and optional dimensions
  (line, machine, operator, shift)

## Alerts

- **AlertRule**: Configurable alert thresholds per factory
- **Alert**: Triggered alerts generated from alert rules

## Relationships (high level)

- Factory 1—\* Line
- Line 1—\* Machine
- Factory 1—\* Operator
- Factory 1—\* Device
- Device 1—\* Event
- Factory 1—\* Event
- Factory 1—\* Shift
- Factory 1—\* DowntimeReason
- Machine 1—\* DowntimeLog
- Factory 1—\* DowntimeLog
- Factory 1—\* KPISnapshot
- Shift 1—\* KPISnapshot (optional)
- Factory 1—\* AlertRule
- AlertRule 1—\* Alert
- Factory 1—\* Alert

## ER Diagram

- Tool: dbdiagram.io
- Diagram link:  
  https://dbdiagram.io/d/6986b1fcbd82f5fce2f25832

## Constraints & Indexes (per guideline)

### Uniqueness

- Factory.code
- Line(factory, code)
- Machine(line, code)
- Operator.employee_id
- Device.device_id
- Event.idempotency_key (nullable)
- DowntimeReason(factory, code)
- Shift(factory, name)
- KPISnapshot(factory, line, machine, operator, snapshot_date, shift)
- AlertRule(factory, name)

### Index Plan

- events(factory_id, timestamp)
- events(device_id, timestamp)
- events(event_type, timestamp)
- events(idempotency_key)
- kpisnapshot(factory_id, snapshot_date)
- kpisnapshot(line_id, snapshot_date)
- alert(factory_id, status, triggered_at)
- device(device_id)
- factory(code, is_active)

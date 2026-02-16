# KPI Formulas (Day-6)

This document describes how KPI values are computed and stored in `KPISnapshot`.

## Scope (Day-6)

Day-6 computes **Line-level daily** KPI snapshots:

- `factory` = set
- `line` = set
- `machine` = NULL
- `operator` = NULL
- `shift` = NULL
- `snapshot_date` = factory-local date

## Time Window (Timezone-safe)

For a given `Factory.timezone` and `snapshot_date` (local date):

- Start = local midnight (00:00) of `snapshot_date`
- End = local midnight (00:00) of next day
  The window is converted to UTC for DB queries.

## Inputs

### Production Events

Source: `apps.devices.models.Event`
Filter:

- `factory_id = factory.id`
- `event_type = "production_cycle"`
- `timestamp >= start_utc AND timestamp < end_utc`
- `device__machine__line_id = line.id`

Payload keys used:

- `payload.output_count` (integer-like)

### Downtime Logs

Source: `apps.monitoring.models.DowntimeLog`
Filter:

- `factory_id = factory.id`
- `started_at >= start_utc AND started_at < end_utc`
- `machine__line_id = line.id`

Field used:

- `duration_minutes`

## KPI Fields

### total_production

Sum of produced units for the line/day:

- `total_production = SUM(Event.payload.output_count)`

### target_production

Simple Day-6 target rule:

- `target_production = Line.capacity_per_hour * 24`
  If `capacity_per_hour` is null/0 then target is 0.

### efficiency_percent

If `target_production > 0`:

- `efficiency_percent = (total_production / target_production) * 100`
  Else:
- `efficiency_percent = NULL`

Stored as Decimal(5,2), so values are rounded to 2 decimal places.

### downtime_minutes

- `downtime_minutes = SUM(DowntimeLog.duration_minutes)`

### uptime_minutes

Day-6 approximation:

- `uptime_minutes = 1440 - downtime_minutes`

(1440 = 24 \* 60 minutes)

### defect_count

Day-6 placeholder (until defect events are implemented):

- `defect_count = 0`

### cycle_time_avg_seconds

Not available in Day-6 because production events currently do not include cycle time in payload.
Stored as:

- `cycle_time_avg_seconds = NULL`

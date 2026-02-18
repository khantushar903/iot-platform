# RBAC Design

## Goal

Role-Based Access Control (RBAC) ensures users can only perform actions allowed for their role.

In this project, a user's role is stored in `accounts.UserProfile.role`.

## Roles

We use four roles:

- **admin**
  - Full access to all actions inside the assigned factory.
  - Can manage users (future), devices, and configuration.
- **manager**
  - Can manage operational resources (devices, machines, alert rules) for the assigned factory.
- **supervisor**
  - Can view operations and manage day-to-day monitoring (alerts, downtime logs).
- **viewer**
  - Read-only access to factory data.

## Role Hierarchy (high to low)

admin > manager > supervisor > viewer

## Permission Rules (high-level)

- **Admin**
  - Create / Update / Delete: factories (future), lines, machines, devices, alert rules
  - View all analytics and reports
- **Manager**
  - Create / Update: lines, machines, devices, alert rules
  - View analytics
- **Supervisor**
  - View lines/machines/devices
  - Create / Update: monitoring logs (downtime logs)
  - View alerts
- **Viewer**
  - View-only for all data

## Implementation Plan

- Authentication: JWT (`/api/auth/login/`, `/api/auth/refresh/`)
- User identity: `UserProfile` links `User` to `Factory` + `role`
- Authorization (next steps):
  - Use DRF permissions (custom permission classes) based on `request.user.userprofile.role`
  - Apply rules per endpoint (e.g., only admin/manager can create devices)

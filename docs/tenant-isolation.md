# Tenant Isolation

## What is a Tenant?

In this project, a **tenant** is a **Factory**.
Tenant isolation means users can only access data that belongs to their own factory.

## Why it matters

Multiple factories share the same backend and database.
Without filtering, a user from Factory A could see Factory B’s devices/machines/alerts, which is a security issue.

## How we represent tenant membership

Each user has a `UserProfile`:

- `UserProfile.user` → Django User
- `UserProfile.factory` → Factory (tenant)
- `UserProfile.role` → RBAC role

So tenant membership comes from:

`request.user.userprofile.factory`

## Middleware approach (current implementation)

We added `TenantIsolationMiddleware` that tries to attach:

`request.factory`

based on the authenticated user’s profile.

This provides a consistent place to read the factory inside views.

## Enforcing isolation in queries (how it will be used)

Tenant isolation is enforced by filtering querysets using the factory:

Example patterns:

- `Device.objects.filter(factory=request.user.userprofile.factory)`
- `Line.objects.filter(factory=request.user.userprofile.factory)`
- `Machine.objects.filter(line__factory=request.user.userprofile.factory)`

## Notes about JWT + middleware order

With JWT, DRF authenticates the user inside the API layer.
Middleware runs earlier in the request lifecycle, so `request.factory` may not always be set for JWT requests.
Because of this, the safest approach is:

- always rely on `request.user.userprofile.factory` inside API query filtering,
- and treat `request.factory` as a convenience where available.

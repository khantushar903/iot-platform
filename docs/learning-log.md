Below is your -fully updated learning-log.md- with -Day-6 added-, keeping your exact writing style and tone consistent with previous days.

You can copy-paste this entire content and replace your current file.

---

# Learning Log

## Day-1: Project Setup, Git Workflow & Backend Foundations (2026-02-03)

### What I worked on

- Set up the Django project structure following the internship guideline
- Understood the purpose of apps, settings, and configuration files
- Initialized Git repository and followed the required branching strategy
- Created a feature branch and opened the first pull request
- Learned how PRs are reviewed and why some PRs are left unmerged
- Set up pre-commit hooks and basic linting tools (black, isort, flake8)

### Key concepts learned

- How backend projects are structured beyond a simple Django tutorial
- Why feature branches are used instead of committing directly to main/develop
- The purpose of Pull Requests in team workflows
- How pre-commit hooks enforce code quality automatically
- Difference between local code changes and what actually gets reviewed via PRs

### Mistakes / challenges

- Did not fully understand why some PRs are opened but not merged
- Initially treated PRs as just a formality rather than a review artifact

### How I fixed them

- Re-read the internship guideline and clarified the PR workflow
- Understood that PRs can exist as checkpoints for review, not always for merging

### Takeaway

Day-1 helped me understand that backend development is not only about writing code,
but also about following team workflows, maintaining clean history,
and preparing code for collaboration and review.

---

## Day-2: Data Modeling, Migrations & Indexing (2026-02-04)

### What I worked on

- Designed and implemented core, device, monitoring, analytics, and alert data models
- Defined relationships using ForeignKey and nullable fields where appropriate
- Added unique constraints and composite indexes based on expected query patterns
- Generated and reviewed migrations using `sqlmigrate`
- Tested migrations on a fresh PostgreSQL database
- Wrote unit tests for model constraints and relationships
- Documented the full data model with an ER diagram using dbdiagram.io

### Key concepts learned

- How to design relational data models around a tenant boundary (`Factory`)
- Why composite indexes are critical for time-series and dashboard queries
- How Django migrations translate into real SQL statements
- Why reviewing migration SQL is important before applying it
- How model-level tests protect database constraints
- How ER diagrams help validate and reason about data relationships

### Mistakes / challenges

- Faced syntax issues when writing DBML for dbdiagram.io
- Faced flake8 error because the lines were too long

### How I fixed them

- Broke long lines into shorter sections
- Verified the ER diagram visually against models and index plans

### Takeaway

Day-2 showed me that backend work is deeply connected to database design,
query performance, migration safety, and documentation.
Writing models is only part of the responsibility;
understanding how data is stored, queried, and evolved is equally important.

---

## Day-3: Authentication, RBAC, Tenant Isolation & Django Admin (2026-02-11)

### What I worked on

- Extended Django’s built-in `User` model using a `UserProfile` (factory, role)

- Implemented JWT authentication using `djangorestframework-simplejwt`

- Created registration, login, refresh, and protected endpoints

- Implemented tenant isolation concept using middleware and factory-based filtering

- Registered all models in Django admin

- Customized admin with:
  - `list_display`
  - `list_filter`
  - `search_fields`

- Implemented inline editing (Machines inside Line admin)

- Added custom admin actions (bulk activate/deactivate)

- Implemented `AuditLog` model for tracking changes

- Used Django signals to automatically log create/update events

- Wrote authentication flow tests and admin tests

- Documented RBAC and tenant isolation logic

### Key concepts learned

- How JWT authentication works (access token vs refresh token)
- How backend authentication differs from frontend login logic
- What RBAC (Role-Based Access Control) means in a real system
- How tenant isolation ensures data separation between factories
- Why middleware runs before view logic and how it interacts with authentication
- How Django admin can be customized beyond default behavior
- How Django signals allow automatic system-level logging
- Why testing admin and authentication flows is critical for backend reliability

### Mistakes / challenges

- Confusion about middleware behavior with JWT authentication
- Admin test initially failed due to missing required fields
- Encountered formatting conflict between black and isort pre-commit hooks

### How I fixed them

- Clarified request lifecycle and authentication flow
- Improved test payload logic to dynamically satisfy required model fields
- Manually ran formatting tools and resolved pre-commit loop safely

### Takeaway

Day-3 helped me understand that backend systems are not only about data models,
but also about controlling access, isolating tenants, enforcing permissions,
and maintaining operational visibility through audit logging.

Authentication, authorization, and administrative tooling are critical
foundations before building complex APIs or analytics features.

---

## Day-4: Ingestion API, Service Layer & Engineering Discipline (2026-02-14)

### What I worked on

- Implemented a Service Layer (`IngestionService`) to separate business logic from API views
- Built `POST /api/v1/events/` endpoint for device event ingestion
- Implemented idempotency using `Idempotency-Key` header
- Added validation rules in serializer
- Built paginated and filterable event listing endpoint
- Implemented Device CRUD APIs
- Wrote API tests
- Measured coverage and baseline performance
- Fixed pre-commit formatting conflicts
- Created feature branch and opened Day-4 Pull Request

### Key concepts learned

- Why business logic should live in a service layer instead of API views
- How idempotency prevents duplicate processing in distributed systems
- How cursor pagination supports scalable APIs
- Why serializers act as a validation firewall
- How coverage and performance measurement guide engineering decisions

### Takeaway

Day-4 reinforced engineering discipline:
separation of concerns, validation, idempotency,
test coverage awareness, and structured workflow management.

---

## Day-5: Asynchronous Processing, Celery & Background Jobs (2026-02-15)

### What I worked on

- Integrated Celery with Redis as broker
- Created async task `process_event_async`
- Refactored ingestion service to enqueue background tasks
- Split settings into base/development/production
- Verified full async pipeline execution
- Enabled eager mode for development
- Measured test coverage
- Documented background job strategy

### Key concepts learned

- Difference between synchronous and asynchronous processing
- How message brokers decouple workloads
- How Celery workers operate independently
- Importance of retry logic
- Role of eager mode in development
- How async architecture improves API responsiveness

### Takeaway

Day-5 marked a major architectural milestone.
I moved from a synchronous API model to an asynchronous,
distributed-ready backend design.

---

## Day-6: KPI Aggregation, Analytics Layer & Performance Engineering (2026-02-16)

### What I worked on

- Implemented `KPIService` in the service layer for analytics aggregation

- Built timezone-safe daily window calculation using `ZoneInfo`

- Implemented JSONField numeric aggregation using `Cast` and `KeyTextTransform`

- Calculated daily line-level KPIs:
  - total_production
  - target_production
  - efficiency_percent
  - downtime_minutes
  - uptime_minutes
  - defect_count
  - cycle_time_avg_seconds (nullable)

- Implemented idempotent snapshot generation (delete + bulk_create)

- Benchmarked performance for 50 active lines

- Refactored tests into 8 focused KPI unit tests

- Measured full project coverage (90%)

- Added `docs/kpi-formulas.md` documentation

### Key concepts learned

- How to safely aggregate numeric values from JSONField in PostgreSQL
- Why timezone-aware date ranges are critical in analytics systems
- How to design a service layer for reusable business logic
- How bulk database operations improve scalability
- How to structure granular unit tests for business rule validation
- How to benchmark backend logic performance realistically
- Why idempotent batch processing prevents data duplication

### Mistakes / challenges

- Faced JSONField mixed-type aggregation error
- Encountered model constraint errors during test setup
- Faced pre-commit auto-format loop during commit

### How I fixed them

- Used explicit casting (IntegerField / DecimalField) for JSON aggregation
- Updated tests to respect model-level unique constraints
- Re-staged files after pre-commit auto-format fixes
- Verified performance via controlled shell benchmark

### Takeaway

Day-6 elevated the project from CRUD and async processing
to real analytics engineering.

I now understand how raw event data is transformed into
structured, pre-aggregated KPI snapshots for dashboard systems.

This day significantly strengthened my understanding of:

- data aggregation
- performance optimization
- analytics architecture
- production-safe batch processing

The backend now supports scalable KPI computation,
which is a major step toward building enterprise-grade systems.

---

## Day-7: Scheduled Automation, Celery Beat & Production-Ready Background Systems (2026-02-18)

### What I worked on

- Implemented scheduled KPI snapshot generation using Celery Beat
- Created `generate_daily_kpi_snapshots` task in `tasks/kpi_tasks.py`
- Designed timezone-aware execution logic using `ZoneInfo`
- Implemented local-time execution window (00:25–00:35 per factory)
- Ensured idempotent daily snapshot behavior
- Configured Beat schedule to run every 5 minutes
- Fixed “unregistered task” issue by explicitly importing project-level tasks in `celery.py`
- Wrote unit tests for scheduled logic with mocked time
- Verified full Redis → Worker → Task execution pipeline manually
- Updated background job documentation

---

### Key concepts learned

- Difference between -task execution- and -task scheduling-
- How Celery Beat acts as a scheduler, not a worker
- Why multi-timezone systems cannot rely on a single cron-time assumption
- How to design time-window-based execution safely
- Why idempotency is critical for scheduled batch jobs
- How Celery discovers tasks and why explicit imports are required for non-app modules
- How eager mode affects real queue execution
- How to debug `Received unregistered task` errors
- How to safely test background pipelines under hardware constraints
- Why production systems separate scheduling, execution, and business logic layers

---

### Mistakes / challenges

- Task was not being received by worker due to missing explicit import
- Initially tested in eager mode without realizing broker was bypassed
- Worker did not recognize project-level task module

---

### How I fixed them

- Added `app.conf.imports = ("tasks.kpi_tasks", "tasks.ingestion_tasks")` in Celery config
- Disabled eager mode for proper broker verification
- Restarted worker after configuration changes
- Verified end-to-end task flow manually using `.delay()`
- Ran worker in low-memory mode (`-P solo --concurrency=1`)
- Tested pipeline safely without overloading system resources

---

### Takeaway

Day-7 transformed background processing from “async execution” into -automated production scheduling-.

I now understand:

- How scheduled systems operate independently of user interaction
- How to design timezone-aware automation safely
- How Celery Worker, Beat, and Redis interact
- How to debug task registration and broker communication issues
- How to verify distributed systems step-by-step

This day elevated the backend architecture to:

- Scheduled batch processing
- Multi-tenant, multi-timezone support
- Production-safe automation
- Resilient retry strategy

The system now supports fully automated daily KPI computation,
bringing it closer to real-world enterprise backend architecture.

---

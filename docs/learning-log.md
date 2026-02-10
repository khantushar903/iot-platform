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

- Break the long lines into short sections
- Verified the ER diagram visually against models and index plans

### Takeaway

Day-2 showed me that backend work is deeply connected to database design,
query performance, migration safety, and documentation.
Writing models is only part of the responsibility;
understanding how data is stored, queried, and evolved is equally important.

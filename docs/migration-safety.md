# Migration Safety Checklist

## Before you merge
- [ ] Run `python manage.py makemigrations --check --dry-run` (ensure no uncommitted model changes)
- [ ] Review SQL using `python manage.py sqlmigrate <app> <migration>`
- [ ] Confirm indexes/constraints are present in generated SQL

## Safe rollout practices (Postgres)
- [ ] Avoid long table locks on large tables
- [ ] Use `CREATE INDEX CONCURRENTLY` for big production tables (requires `atomic = False`)
- [ ] Prefer small, incremental migrations for large datasets
- [ ] Validate migration on a fresh DB

## Verification
- [ ] Apply migrations on a clean database: `python manage.py migrate`
- [ ] Verify indexes exist after migrate (psql `\d <table>`)
- [ ] Record migration apply time and index creation time for reference

## Rollback awareness
- [ ] Know whether a migration is reversible
- [ ] Avoid destructive changes without a migration plan (backfill + deploy strategy)

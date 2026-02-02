# Git Workflow

## Branches

- `main`: stable release branch
- `develop`: integration branch
- `feature/*`: new work (example: `feature/project-init`)
- `fix/*`: bug fixes

## Daily workflow

1. Create a feature branch from `develop`
2. Commit small changes frequently
3. Push the feature branch to GitHub
4. Open a Pull Request into `develop`

## Commit message style

Use short, clear messages:

- `chore: project setup`
- `docs: add setup guide`
- `feat: add devices app`

## Pull Request checklist

- Project runs locally (`python manage.py runserver`)
- Migrations run (`python manage.py migrate`)
- pre-commit passes (`pre-commit run --all-files`)
- Docs updated if needed

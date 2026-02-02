# Learning Log

## 2026-02-02 (Day 1)

### What I did

- Installed and configured Docker Desktop
- Ran Redis in Docker and verified PONG
- Created Django project + apps structure
- Connected Django to PostgreSQL and migrated
- Set up pre-commit (black, isort, flake8)
- Started the server successfully

### Problems I faced + fixes

- PowerShell mkdir syntax issue → used New-Item
- Django couldn’t import apps → fixed AppConfig `name = "apps.<app>"`

### What I learned

- How Django finds apps using import paths
- Why PostgreSQL migrations matter
- What pre-commit does and why teams use it

### Next

- Set up GitHub repo + first PR

# CDOE Complaint Management System

Internal complaint/ticket management tool for the Centre for Distance &
Online Education, University of Mumbai. Runs on a single Windows PC —
no auth, no cloud, no Docker.

**Status: Phase 0 (Project Scaffold) complete.** See
`CDOE_Architecture_Plan.md` for the full architecture and roadmap.

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux (dev machine only)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# then edit .env — Phase 0 only needs SECRET_KEY; IMAP_* values are
# used starting Phase 6

# 4. Run
python run.py
```

Then open **http://127.0.0.1:5000** — you should see the placeholder
dashboard confirming the app, Bootstrap 5, and SQLite wiring all work.

## What exists right now (Phase 0)

- Flask Application Factory (`app/__init__.py`)
- Config loaded from `.env` (`app/config.py`)
- Shared extensions: SQLAlchemy `db`, APScheduler `scheduler` (`app/extensions.py`)
- Three blueprints registered: `dashboard`, `tickets`, `email_sync`
- SQLite configured to write to `instance/cdoe.db` (created automatically)
- Base Jinja template with Bootstrap 5 + Bootstrap Icons via CDN
- Placeholder dashboard page (no real ticket data yet)

## What's NOT built yet

Everything else — models, ticket creation, remarks/status workflow,
timeline, duplicate marking, email sync, search. See the roadmap in
`CDOE_Architecture_Plan.md` (Phases 1–8).

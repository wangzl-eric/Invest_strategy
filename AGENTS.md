# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

IBKR Portfolio Analytics & Quantitative Research Platform — a full-stack Python application with:
- **Backend**: FastAPI on port 8000 (`python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`)
- **Frontend**: Plotly Dash on port 8050 (`python3 frontend/app.py`)

See `README.md` for full architecture, API endpoints, and module reference.

### Running Services

Always set `PYTHONPATH=/workspace` before running backend or frontend.
Add `$HOME/.local/bin` to `PATH` for pip-installed CLI tools (flake8, black, etc.).

```bash
export PYTHONPATH=/workspace
export PATH="$HOME/.local/bin:$PATH"

# Backend (port 8000)
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &

# Frontend (port 8050) — start after backend is ready
python3 frontend/app.py &
```

The backend takes ~10-15s to start because it retries IBKR TWS/Gateway connections (expected to fail in cloud — the app handles this gracefully). Redis is optional and degrades gracefully if unavailable.

### Database

SQLite is the default dev database. Initialize with `python3 scripts/init_db.py` (creates `ibkr_analytics.db`). The `.env` file can be copied from `.env.example` — no secrets are required for basic dev functionality.

### Key Gotchas

- **bcrypt version**: `passlib` is incompatible with `bcrypt>=5.0`. Must use `bcrypt<5` (e.g., `bcrypt==4.3.0`). The update script handles this.
- **email-validator**: Required by pydantic `EmailStr` in auth routes but not listed in `requirements.txt`. Must be installed separately.
- **Dash does NOT hot-reload** from background processes. After code changes to the frontend, kill and restart `frontend/app.py`.
- **Backend `--reload`** works for most code changes, but `.env` changes or new package installs require a full restart.
- **IBKR TWS/Gateway** is not available in cloud. The app handles this gracefully with connection retries and fallback behavior.

### Lint, Test, Build Commands

See `Makefile` for full targets. Quick reference:

| Task | Command |
|------|---------|
| Lint (flake8) | `flake8 backend/ frontend/ portfolio/ backtests/ execution/ --max-line-length=120 --ignore=E501,W503` |
| Format check (black) | `black --check backend/ frontend/ portfolio/ backtests/ execution/ --diff` |
| Tests with coverage | `python3 -m pytest tests/unit/ -v --cov=backend --cov=portfolio --cov=backtests --cov=execution --cov-report=term-missing` |
| All tests | `python3 -m pytest tests/ -v` |

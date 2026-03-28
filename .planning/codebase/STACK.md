# Technology Stack

**Analysis Date:** 2026-03-28

## Languages

**Primary:**
- Python 3.11 — application code under `backend/app/`, tests under `backend/tests/`, tooling in `pyproject.toml` (`target-version = "py311"`, `[tool.mypy] python_version = "3.11"`). CI uses `actions/setup-python@v5` with `python-version: "3.11"` in `.github/workflows/pr-checks.yml` and `.github/workflows/build-publish.yml`.

**Secondary:**
- JavaScript (Node) — example scripts and Jest tests under `scripts/js/` (`sum.js`, `sum.test.js`). Config in `package.json` and `jest.config.js`. No production Node runtime for the Flask API.

## Runtime

**Environment:**
- CPython 3.11 — local dev, CI, and container images built as `python:3.11-slim` (multi-stage) in workflow-generated Dockerfiles inside `.github/workflows/pr-checks.yml` and `.github/workflows/build-publish.yml`.

**Package Manager:**
- pip — install from `backend/requirements.txt` (runtime) and `backend/requirements-dev.txt` (dev, test, lint).
- Lockfile: not present; versions pinned in requirements files (exact pins for main deps, `structlog>=24.1.0` is minimum constraint).

## Frameworks

**Core:**
- Flask 3.0.3 — HTTP API; factory in `backend/app/__init__.py` (`create_app`), WSGI entry `backend/app/main.py` exposing `app` for Gunicorn.
- Gunicorn 22.0.0 — production WSGI server; CI/container CMD binds `0.0.0.0:5000`, 2 workers, 30s timeout (`app.main:app`).
- flask-limiter 3.5.0 — rate limits on items routes; storage `memory://` in `backend/app/__init__.py`.
- structlog (>=24.1.0) — structured logging; configuration in `backend/app/logging_config.py` (JSON vs console via `LOG_FORMAT` / `DEBUG`).
- python-dotenv 1.0.1 — optional local env loading (standard for Flask projects; secrets documented in `.env.example`).

**Testing:**
- pytest 8.3.2 + pytest-cov 5.0.0 — `pyproject.toml` `[tool.pytest.ini_options]` sets `testpaths = ["backend/tests"]`; CI runs with `--cov-fail-under=80`.
- Jest ^29.7.0 — `npm test` / `package.json` scripts; matches `jest.config.js` patterns.

**Build/Dev:**
- Black 24.4.2, isort 5.13.2, Ruff 0.5.6, mypy 1.11.1 — configured in `pyproject.toml` and `.pre-commit-config.yaml`.
- pre-commit — hooks in `.pre-commit-config.yaml` (includes `scripts/check_no_env_committed.py`).
- Bandit 1.7.10 — SAST in `.github/workflows/pr-checks.yml` (`bandit[sarif]`).

## Key Dependencies

**Critical:**
- `flask` — web framework and request lifecycle.
- `gunicorn` — process model for deployed containers.
- `flask-limiter` — abuse protection on public JSON API.
- `structlog` — log shape for aggregators (comment in `logging_config.py` references ELK-style pipelines).

**Infrastructure:**
- stdlib `sqlite3` — only database driver wired in `backend/app/__init__.py` (no SQLAlchemy in `backend/requirements.txt`).
- types-Flask — mypy stubs via `backend/requirements-dev.txt`.

## Configuration

**Environment:**
- Loaded conceptually via `.env` locally (not committed); template and variable list in `.env.example`.
- Application keys built in `backend/app/config.py`: `LOG_LEVEL`, `DEBUG`, `SECRET_KEY`, `SQLITE_PATH`, `DATABASE_URL` (present in config; runtime DB wiring in `create_app` uses SQLite path only — see `INTEGRATIONS.md`).
- Logging toggles: `LOG_FORMAT=json` documented in `.env.example`; `backend/app/__init__.py` derives `json_logs` from env and `DEBUG`.

**Build:**
- No `Dockerfile` or `docker-compose.yml` in the repository root — images are assembled in CI by writing `Dockerfile` and `.dockerignore` in workflow steps (same pattern in `pr-checks.yml` and `build-publish.yml`).
- Python tooling: `pyproject.toml` (Black, isort, Ruff, mypy, pytest); npm tooling: `package.json`, `jest.config.js`.

## Platform Requirements

**Development:**
- Python 3.11, pip, optional Node for Jest (`npm install`, `npm test`).
- Install dev stack: `pip install -r backend/requirements-dev.txt` (per `CLAUDE.md` / pre-commit expectations).

**Production:**
- Container target: Linux amd64 (GitHub-hosted `ubuntu-latest`), non-root user `appuser` (uid 1001) in generated Dockerfile; exposes port 5000.
- Published images: Docker Hub naming `${DOCKERHUB_USERNAME}/${repository.name}` from `.github/workflows/build-publish.yml`.

---

*Stack analysis: 2026-03-28*

# Technology Stack

**Analysis Date:** 2026-03-28

## Languages

**Primary:**
- Python 3.11 — application code under `backend/app/`, tests under `backend/tests/`, scripts under `scripts/`

**Secondary:**
- JavaScript (Node) — example and Jest tests under `scripts/js/` (`sum.js`, `sum.test.js`); optional future `frontend/` tests per `jest.config.js`

## Runtime

**Environment:**
- Python 3.11 — enforced in `.pre-commit-config.yaml` (`default_language_version`, Black hook), `pyproject.toml` (`target-version`, `python_version`), GitHub Actions (`actions/setup-python@v5` with `python-version: "3.11"`), and `Dockerfile.template` (`FROM python:3.11-slim`)

**Package Manager:**
- pip — runtime and dev dependencies; no committed `poetry.lock` or `Pipfile.lock`
- Lockfile: not present; versions pinned in `backend/requirements.txt` and `backend/requirements-dev.txt`

## Frameworks

**Core:**
- Flask 3.0.3 — HTTP API and application factory in `backend/app/__init__.py`
- Gunicorn 22.0.0 — WSGI server in container; entry `app.main:app` per `Dockerfile.template` and `backend/app/main.py`
- flask-limiter 3.5.0 — rate limits on items routes; in-memory storage `memory://` in `backend/app/__init__.py`
- structlog (>=24.1.0) — structured logging in `backend/app/logging_config.py`
- python-dotenv 1.0.1 — local env loading (typical dev workflow; not required inside minimal CI image path)

**Testing:**
- pytest 8.3.2 + pytest-cov 5.0.0 — `pyproject.toml` `[tool.pytest.ini_options]`, CI in `.github/workflows/pr-checks.yml` with `--cov-fail-under=80`
- Jest ^29.7.0 — `package.json` / `jest.config.js` for `scripts/js/**/*.test.js`

**Build/Dev:**
- setuptools (>=68) — `pyproject.toml` `[build-system]` (legacy backend for packaging if used)
- Black 24.4.2, isort 5.13.2, Ruff 0.5.6, mypy 1.11.1 — `backend/requirements-dev.txt` and `.pre-commit-config.yaml`
- types-Flask — stubs for mypy per `backend/requirements-dev.txt` and mypy pre-commit `additional_dependencies`

## Key Dependencies

**Critical:**
- `flask` — web layer and blueprints (`backend/app/infrastructure/http/`)
- `gunicorn` — production process model in `Dockerfile.template` (`--workers 2`, `--timeout 30`)
- `sqlite3` (stdlib) — primary persistence in `backend/app/__init__.py` and `backend/app/infrastructure/persistence/sqlite/`

**Infrastructure:**
- `structlog` — JSON or console rendering driven by `DEBUG` and optional `LOG_FORMAT` in `backend/app/__init__.py`

## Configuration

**Environment:**
- Documented names and intent in `.env.example` (never commit real `.env` files; blocked by `scripts/check_no_env_committed.py` and pre-commit)
- Application keys: `LOG_LEVEL`, `DEBUG`, `SECRET_KEY`, optional `LOG_FORMAT`; database: `SQLITE_PATH`, `DATABASE_URL`; comments for rate limit and placeholder external keys

**Build:**
- `pyproject.toml` — Black, isort, Ruff, mypy, pytest defaults
- `Dockerfile.template` — multi-stage image: builder installs `backend/requirements.txt` into venv; runtime copies `backend/app` only
- `.github/workflows/build-publish.yml` — `sed` substitutes `{{REPO_NAME}}`, `{{GITHUB_REPOSITORY}}`, `{{GITHUB_SHA}}` into generated `Dockerfile`; writes `.dockerignore` inline
- `jest.config.js` — Node test environment and coverage paths

## Platform Requirements

**Development:**
- Python 3.11 virtualenv with `pip install -r backend/requirements-dev.txt`
- Node/npm for `npm test` (Jest) when exercising JS tests
- Optional: pre-commit (`pre-commit install` per `.pre-commit-config.yaml`)

**Production:**
- Container target: Linux image from `python:3.11-slim`, non-root user `appuser`, port 5000 exposed per `Dockerfile.template`
- Registry: Docker Hub (push from `.github/workflows/build-publish.yml` on `main` after Trivy gate)

---

*Stack analysis: 2026-03-28*

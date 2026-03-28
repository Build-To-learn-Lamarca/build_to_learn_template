# External Integrations

**Analysis Date:** 2026-03-28

## APIs & External Services

**Application business APIs:**
- None in the template. The Flask app exposes only its own REST surface (`/health`, `/ready`, `/api/v1/items`). `.env.example` reserves `API_KEY=` as a placeholder for future third-party keys.

**Security scanning (CI):**
- OWASP ZAP Baseline — `zaproxy/action-baseline@v0.14.0` in `.github/workflows/pr-checks.yml` scans `http://localhost:5000` against a container built from the workflow-generated image.
- Bandit — Python SAST; results uploaded via `github/codeql-action/upload-sarif@v3` (category `bandit`).
- Trivy — container image scan using `aquasec/trivy:0.63.0` (Docker socket mount) in `.github/workflows/build-publish.yml`; SARIF upload with category `trivy-image`.

## Data Storage

**Databases:**
- SQLite (file or `:memory:`) — primary persistence. Connection opened in `backend/app/__init__.py` with `sqlite3.connect`; schema via `app.infrastructure.persistence.sqlite` (`init_schema`). Path from `SQLITE_PATH` (default `data/app.db` per `backend/app/config.py`); tests use `:memory:` when `TESTING` is set in config override.
- PostgreSQL / other URLs — `DATABASE_URL` is read in `backend/app/config.py` and documented in `.env.example` and `backend/migrations/README.md` (Alembic guidance). **Not wired** in `create_app`: comments reference future adapters; no outbound TCP client for Postgres in current code.

**File Storage:**
- Local filesystem only — SQLite file under configurable path; directories created with `os.makedirs` for parent of `SQLITE_PATH` when not in-memory.

**Caching:**
- None as a separate service. Rate limiter uses in-memory storage (`storage_uri="memory://"` in `backend/app/__init__.py`).

## Authentication & Identity

**Auth Provider:**
- None. Endpoints listed in workspace docs (`CLAUDE.md`) are unauthenticated. No JWT, OAuth, or session middleware in `backend/app/`.

## Monitoring & Observability

**Error Tracking:**
- No Sentry/Rollbar or similar SDK in `backend/requirements.txt`.

**Logs:**
- structlog + stdlib `logging` in `backend/app/logging_config.py`. JSON logs when `LOG_FORMAT=json` or when not in debug mode (`backend/app/__init__.py`). Suitable for shipping to external log pipelines; no specific vendor integration coded.

## CI/CD & Deployment

**Hosting:**
- Not fixed by repo code. Release artifact is a Docker image pushed to Docker Hub after merge to `main` (`.github/workflows/build-publish.yml`).

**CI Pipeline:**
- GitHub Actions — PR workflow `.github/workflows/pr-checks.yml`: `check-env` (Python script `scripts/check_no_env_committed.py`), `lint-test` (Ruff, mypy, pytest+coverage), `sast` (Bandit), `dast` (Docker build + ZAP). Uses `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`.
- Publish workflow `.github/workflows/build-publish.yml`: `docker/setup-buildx-action@v3`, `docker/build-push-action@v6`, `docker/login-action@v3`, Trivy gate before push.
- Dependabot — `.github/dependabot.yml` for `pip` (`/backend`), `docker` (`/`), `github-actions` (`/`); PRs target branch `homolog`.
- Auto-merge — `.github/workflows/dependabot-automerge.yml` uses `peter-evans/enable-pull-request-automerge@v3` for Dependabot PRs labeled `automerge`.

**Registry:**
- Docker Hub — credentials via org/repo `secrets.DOCKERHUB_TOKEN` and `vars.DOCKERHUB_USERNAME` (documented in template rules; never echo secrets in workflows).

## Environment Configuration

**Required env vars:**
- Production must set `SECRET_KEY` (Flask); `.env.example` uses placeholder. `DEBUG` should remain false in production.

**Operational vars:**
- `LOG_LEVEL`, `SQLITE_PATH`, optional `DATABASE_URL`, optional `LOG_FORMAT`, rate limiting implied via Flask-Limiter defaults and `TESTING` for tests.

**Secrets location:**
- Local: `.env` (gitignored). CI: GitHub Secrets/Variables for Docker Hub. No secrets committed; pre-commit and `check-env` job block `*.env` except `.env.example`.

## Webhooks & Callbacks

**Incoming:**
- None. No Stripe webhooks, GitHub App endpoints, or similar.

**Outgoing:**
- None. No client calls to external HTTP APIs in the core app layer beyond what CI Actions perform.

---

*Integration audit: 2026-03-28*

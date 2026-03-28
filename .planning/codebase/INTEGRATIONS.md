# External Integrations

**Analysis Date:** 2026-03-28

## APIs & External Services

**Application HTTP clients:**
- Not detected — `backend/app/` has no `requests`, `httpx`, or cloud SDK imports; the API is self-contained Flask routes only

**Placeholder configuration:**
- `.env.example` includes commented `API_KEY=` under "External APIs" for derivative projects; no runtime wiring in template code

## Data Storage

**Databases:**
- SQLite (stdlib `sqlite3`) — default path from `SQLITE_PATH` (`backend/app/config.py`, `backend/app/__init__.py`); schema initialization via `backend/app/infrastructure/persistence/sqlite/` and `backend/migrations/001_initial.sql`
- Production hook — `DATABASE_URL` read in `backend/app/config.py`; template still instantiates SQLite in `create_app()`; swapping to PostgreSQL or another backend is a documented extension point (port `ItemRepository`), not implemented as a second driver in-repo

**File Storage:**
- Local filesystem only — SQLite file at configurable path; directories created when not `:memory:` in `backend/app/__init__.py`

**Caching:**
- None for application data — flask-limiter uses in-memory URI `memory://` in `backend/app/__init__.py` (not Redis/Memcached)

## Authentication & Identity

**Auth Provider:**
- Custom / minimal — no OAuth, JWT library, or third-party IdP in dependencies
- Flask `SECRET_KEY` from environment (`backend/app/config.py`, `.env.example`); used for Flask session/signing if enabled downstream; template endpoints listed in `CLAUDE.md` do not enforce API auth

## Monitoring & Observability

**Error Tracking:**
- None — no Sentry/Rollbar SDK in `backend/requirements.txt`

**Logs:**
- structlog to stdout (`backend/app/logging_config.py`) — JSON when production-like (`LOG_FORMAT=json` or non-debug), console renderer in debug; suitable for platform log aggregation but no vendor-specific agent in template

## CI/CD & Deployment

**Hosting:**
- Container image published to Docker Hub — `.github/workflows/build-publish.yml` uses `docker/login-action@v3` with org/repo variables `DOCKERHUB_USERNAME` and secret `DOCKERHUB_TOKEN`; image name `${{ vars.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}`

**CI Pipeline:**
- GitHub Actions — `.github/workflows/pr-checks.yml`: Python lint (Ruff, mypy), pytest with coverage artifact, Bandit SARIF + fail on high confidence, DAST with Docker build from `Dockerfile.template` and OWASP ZAP Baseline (`zaproxy/action-baseline@v0.14.0`) against `http://localhost:5000`
- `.github/workflows/build-publish.yml`: Buildx, Trivy `aquasec/trivy:0.63.0` scan (SARIF to Code Scanning + blocking CRITICAL/HIGH), then push
- Dependabot — `.github/dependabot.yml` for `pip` in `/backend`, `docker` at repo root (base image), and `github-actions` on `/`, targeting branch `homolog`

## Environment Configuration

**Required env vars:**
- Production safety: set `SECRET_KEY` to a strong value (documented in `.env.example`); defaults in `backend/app/config.py` include a dev-only placeholder

**Secrets location:**
- Local: `.env` (gitignored; not read for this audit)
- CI/CD: GitHub Actions secrets/variables (`DOCKERHUB_TOKEN`, `DOCKERHUB_USERNAME` per workflow comments and `build-publish.yml`)

## Webhooks & Callbacks

**Incoming:**
- None — no webhook routes or signature verification in `backend/app/infrastructure/http/routes/`

**Outgoing:**
- None — no callbacks to external systems in application code

---

*Integration audit: 2026-03-28*

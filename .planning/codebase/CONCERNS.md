# Codebase Concerns

**Analysis Date:** 2026-03-28

## Tech Debt

**`DATABASE_URL` documented but unused in wiring:**
- Issue: `get_config()` exposes `DATABASE_URL` in `backend/app/config.py`, and docs describe PostgreSQL, but `create_app()` in `backend/app/__init__.py` always opens SQLite via `sqlite3.connect`. No adapter branch or second repository implementation exists.
- Files: `backend/app/config.py`, `backend/app/__init__.py`, `README.md`, `backend/migrations/README.md`
- Impact: Operators may assume production DB switching works from env alone; it does not without new code.
- Fix approach: Add a factory that selects `SQLiteItemRepository` vs a future Postgres (or SQLAlchemy) implementation based on `DATABASE_URL`; align `.env.example` with actual behavior until then.

**Duplicate schema initialization:**
- Issue: `init_schema()` runs in `create_app()` on the shared connection and again in `SQLiteItemRepository.__init__()` (`backend/app/infrastructure/persistence/sqlite/item_repository.py`).
- Files: `backend/app/__init__.py`, `backend/app/infrastructure/persistence/sqlite/item_repository.py`, `backend/app/infrastructure/persistence/sqlite/schema.py`
- Impact: Redundant work on every repository construction; slightly confusing lifecycle.
- Fix approach: Call `init_schema` only once at app startup (or only inside the repository, not both).

**API validation error shape vs global handlers:**
- Issue: Invalid create-item payloads return `422` with `{"error": "Field 'name' is required"}` from `ItemController` (`backend/app/infrastructure/http/controllers/item_controller.py`), while global handlers in `backend/app/infrastructure/http/error_handlers.py` standardize `400`/`404`/etc. with a `code` field (e.g. `BAD_REQUEST`).
- Files: `backend/app/infrastructure/http/controllers/item_controller.py`, `backend/app/infrastructure/http/error_handlers.py`, `backend/tests/integration/http/test_items.py`
- Impact: Clients see inconsistent error JSON across endpoints; harder to build a single client error model.
- Fix approach: Map validation failures to `400` + shared error schema, or document `422` as intentional and add a `code` field for parity.

## Known Bugs

**Not detected:** No `TODO`/`FIXME`/`HACK`/`XXX` markers in Python, YAML, or JS under the repo root; no clearly broken paths found in static review.

## Security Considerations

**Default `SECRET_KEY` in config:**
- Risk: If `SECRET_KEY` is not set in the environment, Flask uses the default string in `backend/app/config.py` (`dev-secret-change-in-production`), weakening sessions and signed cookies in any deployment that omits the variable.
- Files: `backend/app/config.py`
- Current mitigation: `.env.example` and project docs stress setting `SECRET_KEY`; CI DAST container runs without custom env (still uses in-process default for this minimal API).
- Recommendations: Fail fast at startup when `DEBUG` is false and `SECRET_KEY` equals the dev default, or require `SECRET_KEY` whenever not in `TESTING` mode.

**No authentication or authorization:**
- Risk: All endpoints under `backend/app/infrastructure/http/routes/` are public; anyone who can reach the service can list and create items.
- Files: `backend/app/infrastructure/http/routes/items.py`, `backend/app/infrastructure/http/routes/health.py`
- Current mitigation: Template scope — acceptable for demos; not for multi-tenant or sensitive data.
- Recommendations: Add API keys, JWT, or network-level auth before production use with real data.

**Rate limiting storage and worker model:**
- Risk: `Limiter` in `backend/app/__init__.py` uses `storage_uri="memory://"`. Under Gunicorn with multiple workers (`CMD` in `.github/workflows/pr-checks.yml` and `build-publish.yml` uses `--workers 2`), each process has separate memory; limits are not global per client IP.
- Files: `backend/app/__init__.py`, `.github/workflows/pr-checks.yml`, `.github/workflows/build-publish.yml`
- Current mitigation: Reduces casual abuse in single-process dev; still adds friction.
- Recommendations: Use Redis or another shared store for `flask-limiter` in production.

**Input bounds on `name`:**
- Risk: No max length or charset checks in `CreateItemUseCase` or repository; large payloads could stress SQLite and memory.
- Files: `backend/app/application/use_cases/items/create_item.py`, `backend/app/infrastructure/persistence/sqlite/item_repository.py`
- Recommendations: Enforce max length and reject oversize JSON at the route or controller layer.

## Performance Bottlenecks

**SQLite single shared connection:**
- Problem: One `sqlite3.Connection` per app instance is stored in `app.extensions["db_connection"]` and shared; SQLite allows one writer at a time.
- Files: `backend/app/__init__.py`, `backend/app/infrastructure/persistence/sqlite/item_repository.py`
- Cause: Serialized writes under concurrent POSTs.
- Improvement path: Connection pool or per-request connections with WAL mode for read-heavy workloads; or migrate to PostgreSQL via a real `DATABASE_URL` implementation.

**In-memory rate limiter:**
- Problem: Same as security — `memory://` does not scale across processes and does not survive restarts.
- Files: `backend/app/__init__.py`
- Improvement path: External limiter backend and tuning of default `200 per day` global limit vs per-route limits in `backend/app/infrastructure/http/routes/items.py`.

## Fragile Areas

**CI-defined Docker image (duplication):**
- Files: `.github/workflows/pr-checks.yml` (DAST job), `.github/workflows/build-publish.yml`
- Why fragile: Dockerfile content is embedded in workflow YAML; changing runtime (port, workers, env vars) requires editing two places or builds diverge.
- Safe modification: Edit both workflow steps together; consider extracting a shared composite action or a checked-in `Dockerfile` if drift becomes painful.
- Test coverage: DAST exercises `/health` only indirectly; no automated test that the embedded Dockerfile still matches production intent.

**Global `Exception` handler:**
- Files: `backend/app/infrastructure/http/error_handlers.py`
- Why fragile: Catches all exceptions last; mistakes in error handling or third-party code can mask bugs as generic 500 responses.
- Safe modification: Prefer specific handlers; keep logging as now (`app.logger.exception`).
- Test coverage: No integration test asserting 500 JSON shape from a forced failure path.

## Scaling Limits

**Template API surface:**
- Current capacity: Bounded by single SQLite file (`SQLITE_PATH` from env), single connection, and Gunicorn worker count in CI-generated images.
- Limit: Write contention and disk on one host; rate limits ineffective across workers.
- Scaling path: External DB, shared rate-limit store, horizontal scaling behind a load balancer with health checks (`/health`, `/ready` in `backend/app/infrastructure/http/routes/health.py`).

## Dependencies at Risk

**Pinned vs CI tools:**
- Risk: `pr-checks.yml` installs `bandit[sarif]==1.7.10` while developer deps may differ in `backend/requirements-dev.txt` (verify on bump).
- Files: `.github/workflows/pr-checks.yml`, `backend/requirements-dev.txt`
- Impact: Local Bandit and CI could disagree on rules or SARIF format.
- Migration plan: Pin Bandit in `requirements-dev.txt` and call the same version in Actions.

## Missing Critical Features

**Production database adapter:**
- Problem: No PostgreSQL (or other) repository implementation despite `DATABASE_URL` in config and documentation.
- Blocks: Zero-downtime migrations and multi-instance writes as described in `backend/migrations/README.md` without custom work.

**Structured request logging:**
- Problem: `backend/app/logging_config.py` configures structlog for application code, but HTTP access patterns are not centrally described in reviewed files; operators may rely only on Gunicorn access logs in the container.
- Blocks: Correlation IDs across services without additional middleware.

## Test Coverage Gaps

**Rate limit behavior (429):**
- What's not tested: No test exercises `RATE_LIMIT_EXCEEDED` because `TESTING` disables the limiter (`backend/app/__init__.py`, `backend/tests/conftest.py`).
- Files: `backend/tests/integration/http/test_error_handlers.py` (covers 404/405, not 429/500 paths)
- Risk: Regression in limiter wiring or JSON for 429 could go unnoticed.
- Priority: Medium

**Logging and `main` entry:**
- What's not tested: `backend/app/main.py` `if __name__ == "__main__"` branch and full `configure_logging` branches are largely uncovered by unit/integration layout.
- Files: `backend/app/main.py`, `backend/app/logging_config.py`
- Risk: Low for template usage; higher if custom log sinks are added.

---

*Concerns audit: 2026-03-28*

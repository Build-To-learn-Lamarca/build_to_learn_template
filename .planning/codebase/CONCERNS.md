# Codebase Concerns

**Analysis Date:** 2026-03-28

## Tech Debt

**`DATABASE_URL` configured but not wired:**

- Issue: `get_config()` in `backend/app/config.py` exposes `DATABASE_URL`, and `backend/migrations/README.md` describes PostgreSQL/Alembic paths, but `create_app()` in `backend/app/__init__.py` always opens SQLite via `SQLITE_PATH` (or `:memory:` when testing). Production adopters may assume Postgres works by setting env only.
- Files: `backend/app/config.py`, `backend/app/__init__.py`, `backend/migrations/README.md`
- Impact: Misconfiguration in production (wrong or unused DB settings); Clean Architecture port exists but only one adapter is registered.
- Fix approach: Either wire a second repository implementation when `DATABASE_URL` is set, or remove/stop documenting `DATABASE_URL` until an adapter exists; document the single supported path explicitly in `README.md`.

**Duplicate schema initialization:**

- Issue: `init_schema()` runs in `create_app()` on the shared connection and again in `SQLiteItemRepository.__init__()` for the same connection pattern.
- Files: `backend/app/__init__.py`, `backend/app/infrastructure/persistence/sqlite/item_repository.py`, `backend/app/infrastructure/persistence/sqlite/schema.py`
- Impact: Redundant `CREATE TABLE IF NOT EXISTS` and commits on startup; minor noise, slightly obscures the real initialization point.
- Fix approach: Call `init_schema` only once (factory or repository, not both).

**Readiness probe is a stub:**

- Issue: `/ready` in `backend/app/infrastructure/http/routes/health.py` always returns `{"status": "ready"}` with 200; docstring says to extend for DB/deps but no check runs.
- Files: `backend/app/infrastructure/http/routes/health.py`
- Impact: Orchestrators may route traffic before the DB layer is usable if startup order or disk fails later; false negatives for readiness.
- Fix approach: Ping the SQLite connection (or health-check the configured store) and return 503 on failure.

**Rate limiting vs Gunicorn multi-worker:**

- Issue: `Limiter` uses `storage_uri="memory://"` in `backend/app/__init__.py`, while `Dockerfile.template` runs Gunicorn with `--workers 2`. Each worker process holds separate in-memory limiter state.
- Files: `backend/app/__init__.py`, `Dockerfile.template`
- Impact: Effective per-IP limits are up to N× the configured limits under load; limits are not cluster-coherent if multiple containers run.
- Fix approach: Use Redis (or another shared store) for `flask-limiter` in production, or document that limits are per-process only.

**Validation error shape inconsistent with global errors:**

- Issue: `ItemController.create_item()` in `backend/app/infrastructure/http/controllers/item_controller.py` returns 422 with `{"error": "Field 'name' is required"}` and no `code` field, while `backend/app/infrastructure/http/error_handlers.py` standardizes errors with an optional `code` key (e.g. `BAD_REQUEST`).
- Files: `backend/app/infrastructure/http/controllers/item_controller.py`, `backend/app/infrastructure/http/error_handlers.py`
- Impact: Clients must special-case validation responses; docs that promise a single error contract are misleading.
- Fix approach: Align status (400 vs 422) and body shape with the global handler pattern, or register a dedicated handler for validation.

**Loose dependency pin:**

- Issue: `structlog>=24.1.0` in `backend/requirements.txt` allows floating upgrades; other runtime deps are pinned with `==`.
- Files: `backend/requirements.txt`
- Impact: Non-reproducible builds and harder bisection when logging behavior changes.
- Fix approach: Pin `structlog` to a tested version like other packages.

## Known Bugs

**No tracked in-repo TODO/FIXME markers:**

- Symptoms: `grep` across `*.py` / `*.js` / workflows shows no `TODO`/`FIXME`/`HACK`/`XXX` in application code (only `pass` stubs on `ItemRepository` protocol methods in `backend/app/application/ports/item_repository.py`, which is normal for `Protocol`).
- Files: N/A (absence is the observation)
- Trigger: N/A
- Workaround: N/A

## Security Considerations

**Default `SECRET_KEY`:**

- Risk: `backend/app/config.py` defaults `SECRET_KEY` to `dev-secret-change-in-production` when the env var is missing. Deployments that omit `SECRET_KEY` remain forgeable for session/signing if Flask features that depend on it are enabled later.
- Files: `backend/app/config.py`
- Current mitigation: `.env.example` and docs stress setting secrets; CI blocks committing `.env` via `scripts/check_no_env_committed.py`.
- Recommendations: Fail fast at startup in non-debug environments when `SECRET_KEY` equals the default or is empty; keep `SECRET_KEY` in required production checklist.

**No authentication or authorization:**

- Risk: `GET`/`POST` `/api/v1/items` and health routes are open to any caller on the network boundary.
- Files: `backend/app/infrastructure/http/routes/items.py`, `backend/app/infrastructure/http/routes/health.py`
- Current mitigation: None in application layer (network policy / gateway auth is out of scope for the template).
- Recommendations: Document that the template is intentionally open; add API keys or OIDC when promoting beyond internal demos.

**Development server binding:**

- Risk: `backend/app/main.py` uses `app.run(host="0.0.0.0", port=5000)` for `__main__`, exposing the dev server on all interfaces if used outside a controlled network.
- Files: `backend/app/main.py`
- Current mitigation: Production path is Gunicorn via container; dev use is local responsibility.
- Recommendations: Prefer `127.0.0.1` for local `flask run` patterns or document firewall expectations.

**Ruff security rule relaxations:**

- Risk: `pyproject.toml` ignores `S101` (assert) and `S104` (binding all interfaces) globally for `backend/app` (not only tests). Asserts or `0.0.0.0` binds in app code would not be flagged.
- Files: `pyproject.toml`
- Current mitigation: Bandit runs on `backend/app` in CI with a separate high-confidence gate.
- Recommendations: Narrow `S101`/`S104` ignores to test paths only if the team wants Ruff to enforce those rules in production modules.

## Performance Bottlenecks

**SQLite with multiple Gunicorn workers:**

- Problem: Two worker processes in `Dockerfile.template` each hold a SQLite connection to the same file path (`SQLITE_PATH` under `/app` or mounted volume). SQLite serializes writers; concurrent `POST` traffic can block or raise "database is locked" depending on timeout and journal mode.
- Files: `Dockerfile.template`, `backend/app/__init__.py`, `backend/app/infrastructure/persistence/sqlite/item_repository.py`
- Cause: File-backed SQLite is not ideal for multi-process write concurrency.
- Improvement path: Single worker for SQLite-only deployments, enable WAL + busy timeout, or move to PostgreSQL when `DATABASE_URL` is implemented.

**In-memory rate limiter storage:**

- Problem: See Tech Debt — limits do not aggregate across workers or instances.
- Files: `backend/app/__init__.py`
- Cause: `memory://` storage backend.
- Improvement path: Shared backend for limiter in production.

## Fragile Areas

**DAST job timing:**

- Files: `.github/workflows/pr-checks.yml` (wait loop: 20 iterations × 3s sleep for `/health`).
- Why fragile: Slow cold starts, registry pulls, or resource contention on `ubuntu-latest` can exceed ~60s and fail the job despite a healthy app.
- Safe modification: Tune iteration count/sleep or add a `/health` retry with backoff without reducing security assertions from ZAP.
- Test coverage: Integration tests do not simulate CI container startup; failures appear only in Actions.

**Bandit SARIF upload step:**

- Files: `.github/workflows/pr-checks.yml` (Bandit invoked with `|| true` before upload, then a separate step fails on high severity).
- Why fragile: Upload always receives a SARIF file even when Bandit errors oddly; the real gate is the second invocation. Teams might misread green SARIF upload as "no issues."
- Safe modification: Keep the two-step pattern but document in workflow comments that failure is enforced only in the second step.

**Generic exception handler:**

- Files: `backend/app/infrastructure/http/error_handlers.py` registers `@app.errorhandler(Exception)` after specific handlers.
- Why fragile: Future changes to handler order or Flask upgrades could alter which handler runs for edge-case exceptions; broad handlers are easy to break during refactors.
- Safe modification: Prefer registering handlers from most specific to least; add tests that trigger a non-HTTP exception and assert 500 JSON shape.

## Scaling Limits

**Template API surface:**

- Current capacity: Single-process test app uses `:memory:` SQLite; container image defaults to 2 Gunicorn workers and file SQLite.
- Limit: Throughput bounded by SQLite write serialization and lack of horizontal session/rate-limit state.
- Scaling path: External DB, shared rate-limit store, horizontal replicas behind a load balancer, and real readiness checks.

## Dependencies at Risk

**structlog (unpinned minimum):**

- Risk: See Tech Debt — version drift.
- Impact: Unexpected log format or processor behavior in production.
- Migration plan: Pin in `backend/requirements.txt` after a compatibility test.

## Missing Critical Features

**Production database adapter:**

- Problem: No Postgres (or other) repository implementation despite configuration hints.
- Blocks: Multi-instance write scaling and org-standard DB operations without custom forks.

**Input bounds on `name`:**

- Problem: No max length or charset validation on item names in `CreateItemUseCase` or controller; large JSON bodies could stress SQLite and memory.
- Blocks: Safe public exposure without a reverse proxy body limit.

## Test Coverage Gaps

**Global 500 / unhandled exception JSON:**

- What's not tested: No integration test asserts `register_error_handlers` 500 or generic `Exception` path returns `INTERNAL_ERROR` JSON.
- Files: `backend/app/infrastructure/http/error_handlers.py`, `backend/tests/integration/http/test_error_handlers.py`
- Risk: Regressions in error handler registration could leak stack traces or wrong status codes unnoticed.
- Priority: Medium

**Rate limiting behavior:**

- What's not tested: No test exercises 429 responses when limits are exceeded (limiter disabled when `TESTING` is true in `create_app`).
- Files: `backend/app/__init__.py`, `backend/app/infrastructure/http/routes/items.py`
- Risk: Misconfigured limits or disabled limiter in production could go undetected.
- Priority: Low for template; higher if SLA requires abuse protection.

**Readiness vs database:**

- What's not tested: `/ready` always succeeds; no test ties readiness to DB connectivity.
- Files: `backend/app/infrastructure/http/routes/health.py`, `backend/tests/integration/http/test_health.py` (if extended)
- Risk: False confidence in K8s readiness probes.
- Priority: Medium for container orchestration users

**mypy scope:**

- What's not tested: `pyproject.toml` sets `files = ["backend/app"]` for mypy; `backend/tests` are not type-checked under the same strict profile.
- Files: `pyproject.toml`, `backend/tests/**/*.py`
- Risk: Test helpers drift from typing expectations until runtime failures.
- Priority: Low

---

*Concerns audit: 2026-03-28*

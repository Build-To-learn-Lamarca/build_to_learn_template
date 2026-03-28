# Testing Patterns

**Analysis Date:** 2026-03-28

## Test Framework

**Runner:**
- **pytest** 8.3.2 (pinned in `backend/requirements-dev.txt`).
- Config: `pyproject.toml` → `[tool.pytest.ini_options]`: `testpaths = ["backend/tests"]`, `python_files = ["test_*.py", "*_test.py"]`, `python_functions = ["test_*"]`, `addopts = "-v --tb=short"`.

**Assertion Library:**
- Plain `assert` (pytest introspection). `pytest.raises` for expected exceptions.

**Run Commands:**
```bash
# From repo root (path + conftest add backend to sys.path)
pytest

# Verbose / short tracebacks already default via addopts
pytest backend/tests

# Match CI: coverage on application package, XML report, gate
pytest --cov=backend/app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80
```

**JavaScript (template example):**
```bash
npm test
```
Runs Jest per `package.json` (`"test": "jest"`). **CI:** `.github/workflows/pr-checks.yml` does not invoke `npm test`; only Python lint + pytest + Bandit + DAST are automated on PRs.

## Test File Organization

**Location:**
- Python tests live under `backend/tests/`, split into `unit/` and `integration/http/`, mirroring Clean Architecture layers for unit tests.

**Naming:**
- Files: `test_<module>.py` (e.g. `test_create_item.py`, `test_health.py`).
- Classes: `Test<Feature>` (e.g. `TestCreateItemUseCase`, `TestHealthEndpoint`).
- Methods: `test_<behavior>` (snake_case); Ruff `N802` is ignored in tests for this pattern.

**Structure:**
```
backend/tests/
├── conftest.py              # app + client fixtures
├── unit/
│   ├── application/
│   │   ├── fakes.py         # InMemoryItemRepository, FailingItemRepository
│   │   └── use_cases/
│   ├── domain/
│   │   └── entities/
│   └── infrastructure/
│       └── persistence/
└── integration/
    └── http/
```

## Test Structure

**Suite Organization:**
- Group related cases in a class with a docstring describing the feature under test.

```python
class TestCreateItemUseCase:
    """CreateItemUseCase persists item and returns it."""

    def test_creates_item_with_auto_id(self) -> None:
        """First item gets id 1, second gets id 2."""
        repo = InMemoryItemRepository()
        use_case = CreateItemUseCase(repo)
        req = CreateItemRequest(name="Widget")
        result = use_case.execute(req)
        assert result.id == 1
        assert result.name == "Widget"
```

**Patterns:**
- **Arrange–Act–Assert:** Build fakes/repo and use case, call `execute` or HTTP client, assert on entities or `response.status_code` / `get_json()`.
- **Fixtures:** Shared `app` and `client` in `backend/tests/conftest.py`; local `@pytest.fixture` in `test_sqlite_item_repository.py` for `sqlite_repo`.
- **Typing:** Test functions annotated with `-> None`; integration tests type `client` as `FlaskClient`.

## Mocking

**Framework:** No `unittest.mock` or `pytest-mock` required in the current suite; **fake implementations** are preferred for ports.

**Patterns:**
- `InMemoryItemRepository` and `FailingItemRepository` in `backend/tests/unit/application/fakes.py` implement the same methods as `ItemRepository` without a mocking library.

```python
def test_propagates_repository_exception_on_add(self) -> None:
    repo = FailingItemRepository()
    use_case = CreateItemUseCase(repo)
    with pytest.raises(RuntimeError, match="repository add failed"):
        use_case.execute(CreateItemRequest(name="X"))
```

**What to Mock:**
- Not applicable as a rule; use fakes for `ItemRepository` in unit tests.

**What NOT to Mock:**
- Integration tests use real `create_app` wiring with in-memory SQLite (`TESTING: True` → `db_path = ":memory:"` in `backend/app/__init__.py`), so DB and routes are exercised end-to-end for HTTP tests.

## Fixtures and Factories

**Test Data:**
- Domain entities built inline: `Item(id=0, name="Widget")`, `CreateItemRequest(name="Widget")`.
- SQLite unit tests use `sqlite3.connect(":memory:")` inside a fixture returning `SQLiteItemRepository`.

**Location:**
- Global fixtures: `backend/tests/conftest.py` (`app`, `client`).
- Module-scoped fixtures: e.g. `sqlite_repo` in `backend/tests/unit/infrastructure/persistence/test_sqlite_item_repository.py`.

## Coverage

**Requirements:** CI enforces **≥ 80%** line coverage on `backend/app` via `--cov-fail-under=80` in `.github/workflows/pr-checks.yml` (`lint-test` job).

**View Coverage:**
```bash
pytest --cov=backend/app --cov-report=term-missing --cov-fail-under=80
```

Artifacts: workflow uploads `coverage.xml` as `coverage-report-${{ github.run_id }}` (retention 7 days).

## Test Types

**Unit Tests:**
- **Domain:** `backend/tests/unit/domain/entities/test_item.py` (entity behavior).
- **Application:** `backend/tests/unit/application/use_cases/` — use cases with fakes; failure paths assert propagated exceptions.
- **Infrastructure:** `backend/tests/unit/infrastructure/persistence/test_sqlite_item_repository.py` — repository against in-memory SQLite (not the Flask app).

**Integration Tests:**
- **HTTP:** `backend/tests/integration/http/` — `FlaskClient` against `create_app` with `TESTING=True`: health/ready, items API, error handler JSON shapes.

**E2E Tests:**
- Not used; DAST (OWASP ZAP) runs against a running app in CI separately from pytest.

## Common Patterns

**Async Testing:**
- Not applicable; stack is synchronous Flask WSGI.

**Error Testing:**
```python
with pytest.raises(RuntimeError, match="repository list failed"):
    use_case.execute()
```

**HTTP JSON assertions:**
```python
response = client.get("/health")
assert response.get_json() == {"status": "ok"}
```

**JavaScript (Jest):**
- Config: `jest.config.js` — `testEnvironment: "node"`, `testMatch` includes `**/scripts/js/**/*.test.js` and optional `frontend/**/*.test.js`.
- Example: `scripts/js/sum.test.js` uses `describe` / `it` / `expect(...).toBe(...)`.
- Coverage collection paths: `scripts/js/**/*.js`, `frontend/src/**/*.js` (output dir `coverage-js`).

---

*Testing analysis: 2026-03-28*

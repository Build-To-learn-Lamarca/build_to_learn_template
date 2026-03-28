# Testing Patterns

**Analysis Date:** 2026-03-28

## Test Framework

**Runner:**
- **pytest** 8.3.2 — declared in `backend/requirements-dev.txt`.
- Config: `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["backend/tests"]`, `python_files = ["test_*.py", "*_test.py"]`, `python_functions = ["test_*"]`, `addopts = "-v --tb=short"`.

**Assertion Library:**
- Plain `assert` with pytest’s introspection.

**Run Commands:**
```bash
pytest                              # From repo root (uses pyproject.ini_options)
pytest backend/tests/               # Explicit path
pytest backend/tests/integration/http/test_items.py -v
npm test                            # Jest — see JavaScript below
```

## Coverage

**Requirements:** CI enforces **80%** minimum line coverage on `backend/app` — `.github/workflows/pr-checks.yml` (`pytest ... --cov=backend/app ... --cov-fail-under=80`).

**Reports:** Terminal missing lines and XML at `coverage.xml` for upload in the same workflow.

**Local coverage:**
```bash
pytest --cov=backend/app --cov-report=term-missing --cov-fail-under=80
```

## Test File Organization

**Location:**
- **Unit:** `backend/tests/unit/` mirrors Clean Architecture — `domain/`, `application/`, `infrastructure/`.
- **Integration (HTTP):** `backend/tests/integration/http/`.

**Naming:**
- `test_<module_or_feature>.py`; test classes `Test<Feature>`; methods `test_<behavior>`.

**Structure:**
```
backend/tests/
├── conftest.py
├── integration/http/
│   ├── test_error_handlers.py
│   ├── test_health.py
│   └── test_items.py
└── unit/
    ├── application/fakes.py
    ├── application/use_cases/test_create_item.py
    ├── domain/entities/test_item.py
    └── infrastructure/persistence/test_sqlite_item_repository.py
```

## Test Structure

**Suite Organization:**
- Classes group related scenarios (e.g. `TestListItems`, `TestCreateItem` in `backend/tests/integration/http/test_items.py`).
- Docstrings on classes and tests describe the behavior under test (`backend/tests/unit/domain/entities/test_item.py`).

**Patterns:**
- **Arrange–Act–Assert** via straight-line code without a formal framework; integration tests use the `client` fixture from `backend/tests/conftest.py`.

**Shared fixtures:**
- `app` — `create_app({"TESTING": True, "DEBUG": False})` — `backend/tests/conftest.py`.
- `client` — `app.test_client()` with `# type: ignore[union-attr]` for mypy.

## Mocking

**Framework:** No `unittest.mock` in current suite; **test doubles** live in `backend/tests/unit/application/fakes.py`.

**Patterns:**
```python
# InMemoryItemRepository — happy path
# FailingItemRepository — raises RuntimeError on list/add
```
Import fakes in use case tests: `from tests.unit.application.fakes import FailingItemRepository, InMemoryItemRepository` — `backend/tests/unit/application/use_cases/test_create_item.py`.

**What to Mock:**
- Port implementations (`ItemRepository`) via fakes or in-memory adapters for unit tests.

**What NOT to Mock:**
- Domain entities in entity tests — construct real `Item` instances (`backend/tests/unit/domain/entities/test_item.py`).

## Fixtures and Factories

**Test data:**
- DTOs built inline: `CreateItemRequest(name="Widget")`.
- Domain: `Item(id=..., name=...)` for repository tests.

**Local fixtures:**
- `sqlite_repo` in `backend/tests/unit/infrastructure/persistence/test_sqlite_item_repository.py` — `@pytest.fixture` yielding `SQLiteItemRepository` over `:memory:` SQLite.

**Location:**
- Shared: `backend/tests/conftest.py`.
- Layer-specific fakes: `backend/tests/unit/application/fakes.py`.

## JavaScript (Jest)

**Runner:** Jest 29.x — `package.json` (`"test": "jest"`), `jest.config.js`.

**Config highlights:**
- `testEnvironment: "node"`.
- `testMatch`: `**/scripts/js/**/*.test.js`, `**/frontend/**/*.test.js`, `**/*.test.js`.
- Coverage collected from `scripts/js/**/*.js` and `frontend/src/**/*.js` into `coverage-js/`.

**Example pattern:**
```javascript
describe("sum", () => {
  it("adds two numbers", () => {
    expect(sum(1, 2)).toBe(3);
  });
});
```
Reference: `scripts/js/sum.test.js` (requires `./sum`).

**CI note:** `.github/workflows/pr-checks.yml` runs pytest with coverage; **Jest is not invoked in that workflow** — run `npm test` locally for JS tests unless another job is added.

## Test Types

**Unit tests:**
- Domain rules and equality (`backend/tests/unit/domain/entities/test_item.py`).
- Use cases with in-memory or failing repos (`backend/tests/unit/application/use_cases/`).
- SQLite repository against `:memory:` connection (`backend/tests/unit/infrastructure/persistence/test_sqlite_item_repository.py`).

**Integration tests:**
- Full Flask app + client: health, items API, global error handlers — `backend/tests/integration/http/test_health.py`, `test_items.py`, `test_error_handlers.py`.

**E2E:** Not used in this template.

## Common Patterns

**HTTP integration:**
```python
response = client.get("/api/v1/items")
assert response.status_code == 200
assert response.get_json() == []
```

**Failure path:**
```python
with pytest.raises(RuntimeError, match="repository add failed"):
    use_case.execute(CreateItemRequest(name="X"))
```

**Error JSON shape:**
- Assert `status_code`, then `response.get_json()` keys `error` and `code` — `backend/tests/integration/http/test_error_handlers.py`.

---

*Testing analysis: 2026-03-28*

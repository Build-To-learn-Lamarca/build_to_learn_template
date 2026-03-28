# Coding Conventions

**Analysis Date:** 2026-03-28

## Naming Patterns

**Files:**
- Python modules and packages use `snake_case`: `item_repository.py`, `create_item.py`, `error_handlers.py`.
- Test modules mirror the area under test: `test_create_item.py`, `test_sqlite_item_repository.py`.
- JavaScript example modules use `camelCase` for exports where idiomatic (`sum.js` + `sum.test.js`).

**Functions:**
- Module-level and method names use `snake_case`: `create_app`, `register_error_handlers`, `execute`.
- Private-by-convention attributes on classes use a single leading underscore: `_repository`, `_list_items`, `_items`.

**Variables:**
- `snake_case` for locals and parameters (`request`, `sqlite_repo`, `test_app`).
- Configuration keys follow Flask/env style where applicable (`TESTING`, `DEBUG`, `SQLITE_PATH` in `create_app` config dict).

**Types:**
- Classes use `PascalCase`: `Item`, `CreateItemUseCase`, `ItemController`, `SQLiteItemRepository`, `InMemoryItemRepository`.
- DTOs and responses: `CreateItemRequest`, `ItemResponse`.
- Protocols name the capability: `ItemRepository` in `backend/app/application/ports/item_repository.py`.

## Code Style

**Formatting:**
- **Black** — line length 88, target Python 3.11. Config: `pyproject.toml` `[tool.black]`. Excludes `.venv`, `venv`, `__pycache__`, `.git`.
- **isort** — `profile = "black"`, `line_length = 88`, first-party package `app`, `src_paths = ["backend"]`.

**Linting:**
- **Ruff** — `src = ["backend"]`, targets py311. Selected rule groups: `E`, `W`, `F`, `B`, `C4`, `UP`, `S`, `N`. Ignores globally: `E501` (line length delegated to Black), `S101` (assert in tests), `S104` (binding all interfaces).
- **Per-file ignores:** `backend/tests/**/*.py` → `S` (bandit-style) and `N802` (pytest method names); `backend/tests/conftest.py` → `E402` (imports after path manipulation).

**Type checking:**
- **mypy** — `strict = true` for `backend/app` only (`files = ["backend/app"]` in `pyproject.toml`). Flask/Werkzeug stubs: `ignore_missing_imports = true` in overrides.
- Tests are not in mypy’s `files` list; production code under `backend/app` is the typed surface.

## Import Organization

**Order (enforced by isort + Black profile):**
1. `from __future__ import annotations` when present (first).
2. Standard library.
3. Third-party (e.g. `pytest`, `flask`, `sqlite3`, `structlog`).
4. First-party `app.*` (known first party in `pyproject.toml`).
5. Test-only imports such as `tests.unit.application.fakes` in test modules.

**Path resolution:**
- `backend/tests/conftest.py` inserts `backend` on `sys.path` so imports use `app` and `tests` from repo root or `backend/` runs. Do not duplicate this pattern unless adding another test entrypoint.

**Path aliases:**
- No TypeScript path aliases in use; Python resolves `app` as the package under `backend/`.

## Error Handling

**HTTP / API layer:**
- Global handlers live in `backend/app/infrastructure/http/error_handlers.py`: `register_error_handlers` registers 400, 404, 405, 429, 500, plus a catch-all `Exception` → 500 JSON with `INTERNAL_ERROR`.
- Helper `_error_response` builds bodies `{"error": "...", "code": "..."}` consistently.
- Unhandled paths log with `app.logger.exception` before returning 500.

**Controller validation:**
- `ItemController.create_item` in `backend/app/infrastructure/http/controllers/item_controller.py` returns `(dict, status)`; validation failures use 422 and ad-hoc `{"error": "Field 'name' is required"}` (not the same shape as global error codes — intentional split between validation vs framework errors).

**Application / domain:**
- Use cases do not catch repository failures; they propagate exceptions (see tests in `backend/tests/unit/application/use_cases/` using `FailingItemRepository`).

## Logging

**Framework:** `structlog` configured in `backend/app/logging_config.py` via `configure_logging`.

**Patterns:**
- `create_app` in `backend/app/__init__.py` chooses JSON vs console from `LOG_FORMAT` and `DEBUG`.
- Use `structlog.get_logger()` in application code (per module docstring in `logging_config.py`). Flask’s `app.logger` is used for exception paths in error handlers.

## Comments

**When to comment:**
- Module docstrings state purpose (`"""Application factory — Clean Architecture wiring."""`).
- Class docstrings summarize responsibility (`"""Creates an item and persists it via the repository."""`).
- Inline comments are sparse; prefer clear names.

**JSDoc/TSDoc:**
- JavaScript example in `scripts/js/` uses short block comments above the test file purpose, not formal JSDoc.

## Function Design

**Size:** Small, single-purpose methods (`execute`, `list_items`, `create_item`).

**Parameters:**
- Use cases take a repository in `__init__` and DTOs or no args in `execute`.
- Controllers take already-parsed DTOs or `None` for bad JSON.

**Return Values:**
- Use cases return domain entities (`Item`) or lists of entities.
- Controllers return `tuple[body, http_status]` for routes to unpack.

## Module Design

**Exports:**
- Use cases are re-exported from `backend/app/application/use_cases/__init__.py` for stable imports (`CreateItemUseCase`, `ListItemsUseCase`).

**Barrel files:**
- Package `__init__.py` files under `backend/tests` are mostly empty markers; domain/application structure uses explicit submodule imports.

---

*Convention analysis: 2026-03-28*

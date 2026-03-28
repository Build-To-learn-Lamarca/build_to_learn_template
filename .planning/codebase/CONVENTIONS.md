# Coding Conventions

**Analysis Date:** 2026-03-28

## Naming Patterns

**Files:**
- Python modules: `snake_case.py` under `backend/app/` mirroring layers — e.g. `backend/app/domain/entities/item.py`, `backend/app/application/use_cases/items/create_item.py`, `backend/app/infrastructure/http/controllers/item_controller.py`.
- Test modules: `test_*.py` alongside the layer under `backend/tests/unit/` or `backend/tests/integration/http/`.

**Functions:**
- `snake_case` for functions and methods; use case entry points use `execute()` (see `backend/app/application/use_cases/items/create_item.py`).

**Variables:**
- `snake_case` for locals and parameters; private instance attributes use a single leading underscore where needed (e.g. `self._list_items` in `backend/app/infrastructure/http/controllers/item_controller.py`).

**Types:**
- PEP 585 built-in generics (`list[str]`, `dict[str, Any]`); union syntax `X | Y` with `from __future__ import annotations` at file top (pattern in `backend/app/infrastructure/http/error_handlers.py`, `backend/app/infrastructure/http/controllers/item_controller.py`).

**Classes:**
- `PascalCase` for classes (`Item`, `ItemController`, `CreateItemUseCase`).

## Code Style

**Formatting:**
- **Black** — line length 88, target Python 3.11, excludes venv/`__pycache__` — configured in `pyproject.toml` (`[tool.black]`).
- Pre-commit runs Black with `--config pyproject.toml` on `^backend/` — see `.pre-commit-config.yaml`.

**Import sorting:**
- **isort** with `profile = "black"`, `known_first_party = ["app"]`, `src_paths = ["backend"]` — `pyproject.toml` `[tool.isort]`.
- Aligns with Ruff’s isort integration via `[tool.ruff.lint.isort]`.

**Linting:**
- **Ruff** — `src = ["backend"]`, `target-version = "py311"`, line length 88 — `pyproject.toml` `[tool.ruff]` and `[tool.ruff.lint]`.
- Rule families: `E`, `W`, `F`, `B`, `C4`, `UP`, `S`, `N`; ignored globally: `E501`, `S101`, `S104`.
- Per-file: `backend/tests/**/*.py` relaxes `S` and `N802`; `backend/tests/conftest.py` allows `E402` (import after path manipulation) — `pyproject.toml` `[tool.ruff.lint.per-file-ignores]`.

**Type checking:**
- **mypy** `strict = true` on `files = ["backend/app"]` — `pyproject.toml` `[tool.mypy]`.
- Third-party gaps: `flask.*` and `werkzeug.*` use `ignore_missing_imports` in overrides.
- Pre-commit mypy hook scopes to `^backend/app/` with Flask stubs — `.pre-commit-config.yaml`.

## Import Organization

**Order:**
1. `from __future__ import annotations` when used (first line after module docstring).
2. Standard library.
3. Third party (e.g. `flask`, `pytest`, `structlog`).
4. First-party `app.*` — Ruff/isort treat `app` as first party.

**Path resolution:**
- Tests insert `backend` on `sys.path` in `backend/tests/conftest.py` before importing `app`; Ruff allows `E402` only there.

## Error Handling

**HTTP / API layer:**
- Global handlers in `backend/app/infrastructure/http/error_handlers.py` return JSON with `error` and optional `code` via `register_error_handlers()`.
- Unhandled exceptions and 500 paths log with `app.logger.exception()` before returning standardized JSON.

**Application / domain:**
- Use cases propagate repository failures; tests expect propagation with `pytest.raises` — see `backend/tests/unit/application/use_cases/test_create_item.py` (`FailingItemRepository`).

**Controller validation:**
- `ItemController.create_item()` returns `422` with a dict body for invalid input instead of raising — `backend/app/infrastructure/http/controllers/item_controller.py`.

## Logging

**Framework:** structlog configured in `backend/app/logging_config.py` via `configure_logging()`.

**Patterns:**
- `create_app()` in `backend/app/__init__.py` chooses JSON vs console from `LOG_FORMAT` / `DEBUG`.
- Standard `logging` is also configured for library loggers; Flask `app.logger` used in error handlers for exceptions.

## Comments

**When to Comment:**
- Module-level docstrings describe purpose (`backend/app/logging_config.py`, test modules).
- Inline comments are sparse; behavior is expressed through tests and type hints.

**Docstrings:**
- Present on public factory functions (`create_app`, `register_error_handlers`, `configure_logging`) and test classes where they clarify scope.

## Function Design

**Size:** Small, focused methods on controllers and use cases; controllers return `(body, status_code)` tuples.

**Parameters:**
- DTOs for use case input (`CreateItemRequest` from `backend/app/application/dto/item_dto.py`).

**Return Values:**
- Use cases return domain entities or DTOs; controllers serialize to `dict` for JSON.

## Module Design

**Exports:**
- Use cases re-exported from `backend/app/application/use_cases/__init__.py` for convenient imports in `backend/app/__init__.py`.

**Barrel files:**
- Application package `__init__.py` wires Flask only; domain stays free of framework imports.

---

*Convention analysis: 2026-03-28*

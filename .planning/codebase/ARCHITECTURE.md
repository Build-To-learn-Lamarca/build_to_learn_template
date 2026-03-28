# Architecture

**Analysis Date:** 2026-03-28

## Pattern Overview

**Overall:** Clean Architecture with Domain-Driven Design (DDD) boundaries inside a single Flask application package.

**Key Characteristics:**
- Dependency rule: `infrastructure` → `application` → `domain`; `domain` has no imports from outer layers.
- Application factory (`create_app`) wires SQLite connection, repository, use cases, controller, limiter, and blueprints in one place (`backend/app/__init__.py`).
- HTTP concerns split: blueprints parse requests and return Flask responses; controllers translate to/from use-case DTOs and return `(body, status)` tuples.
- Persistence is behind a `Protocol` port (`ItemRepository`); the default adapter is SQLite (`SQLiteItemRepository`).

## Layers

**Domain:**

- Purpose: Core entities and value objects with no framework or I/O.
- Location: `backend/app/domain/`
- Contains: Frozen dataclass entities (e.g. `Item`).
- Depends on: Standard library only (e.g. `dataclasses`).
- Used by: `application` (use cases, DTOs) and `infrastructure` (repository implementations).

**Application:**

- Purpose: Use cases, input/output DTOs, and persistence ports (interfaces).
- Location: `backend/app/application/`
- Contains: `ports/` (`ItemRepository` Protocol), `use_cases/items/` (`CreateItemUseCase`, `ListItemsUseCase`), `dto/` (`CreateItemRequest`, `ItemResponse`).
- Depends on: `domain` and typing (`Protocol`).
- Used by: `infrastructure` controllers and `create_app` wiring.

**Infrastructure:**

- Purpose: Framework adapters — HTTP (Flask blueprints, controllers, error handlers) and persistence (SQLite schema + repository).
- Location: `backend/app/infrastructure/`
- Contains: `http/` (routes, controllers, `error_handlers.py`), `persistence/sqlite/` (`schema.py`, `item_repository.py`).
- Depends on: Flask, flask-limiter, sqlite3, `application`, `domain`.
- Used by: `create_app` in `backend/app/__init__.py`.

**Composition root (application bootstrap):**

- Purpose: Construct the graph of objects and register Flask extensions.
- Location: `backend/app/__init__.py` (`create_app`), `backend/app/main.py` (module-level `app` for gunicorn).
- Contains: Config merge, structlog setup, DB connection, repository and use-case instantiation, `ItemController`, `Limiter`, `register_error_handlers`, blueprint registration.

## Data Flow

**HTTP request → list items:**

1. Flask matches `GET /api/v1/items` on blueprint from `backend/app/infrastructure/http/routes/items.py`.
2. Route handler calls `ItemController.list_items()` in `backend/app/infrastructure/http/controllers/item_controller.py`.
3. Controller runs `ListItemsUseCase.execute()` (`backend/app/application/use_cases/items/list_items.py`), which calls `ItemRepository.list()`.
4. `SQLiteItemRepository.list()` (`backend/app/infrastructure/persistence/sqlite/item_repository.py`) reads rows and maps to `Item` entities.
5. Controller maps entities to `ItemResponse` and returns a list of dicts with status `200`; route wraps with `jsonify`.

**HTTP request → create item:**

1. `POST /api/v1/items` in `items.py` parses JSON into `CreateItemRequest` (or passes `None` / invalid shape).
2. `ItemController.create_item()` validates name; on failure returns `422` with a small error dict (not the global error-handler shape).
3. On success, `CreateItemUseCase.execute()` builds `Item(id=0, name=...)` and `repository.add()` persists and returns `Item` with real id.
4. Controller returns `ItemResponse` as dict with `201`.

**State Management:**

- No global mutable domain state. Per-process SQLite connection stored on `app.extensions["db_connection"]` in `create_app`. Rate limiter kept on `app.extensions["limiter"]` to avoid GC of weakly referenced limiter.

## Key Abstractions

**ItemRepository (port):**

- Purpose: Define persistence contract for the `Item` aggregate without coupling to SQLite.
- Examples: `backend/app/application/ports/item_repository.py` (Protocol), `backend/app/infrastructure/persistence/sqlite/item_repository.py` (implementation).
- Pattern: Ports and adapters; `typing.Protocol` for structural subtyping.

**Use cases:**

- Purpose: Single responsibility application services orchestrating domain + repository.
- Examples: `backend/app/application/use_cases/items/create_item.py`, `list_items.py`.
- Pattern: Class with `execute()` method; constructor receives `ItemRepository`.

**ItemController:**

- Purpose: Boundary between HTTP-agnostic use cases and response shaping (dicts + status codes).
- Examples: `backend/app/infrastructure/http/controllers/item_controller.py`.
- Pattern: Thin adapter; no Flask imports inside controller (only DTOs and use cases).

**Blueprint factories:**

- Purpose: Inject controller and limiter where routes need them.
- Examples: `create_items_blueprint` in `backend/app/infrastructure/http/routes/items.py`; static `health_bp` in `backend/app/infrastructure/http/routes/health.py`.
- Pattern: Factory function returns configured `Blueprint`; re-exported from `backend/app/infrastructure/http/routes/__init__.py`.

## Entry Points

**Development / CLI:**

- Location: `backend/app/main.py`
- Triggers: `python -m app.main` from `backend/` (with `PYTHONPATH` or cwd set) or direct run of `__main__` block.
- Responsibilities: `app = create_app()`; optional `app.run(host="0.0.0.0", port=5000)`.

**Production (container / gunicorn):**

- Location: `backend/app/main.py` — WSGI callable `app`
- Triggers: `gunicorn ... app.main:app` (see `Dockerfile.template` `CMD`).
- Responsibilities: Same `create_app()` instance as dev; binding and workers are process-manager concerns.

**Tests:**

- Location: `backend/tests/conftest.py` imports `create_app` and builds app with `{"TESTING": True, "DEBUG": False}`.
- Triggers: pytest discovers `backend/tests/` per `pyproject.toml` `[tool.pytest.ini_options]`.

## Error Handling

**Strategy:** Flask global error handlers for standard HTTP errors; controller-level validation for create-item field errors; logging on 500 and unhandled exceptions.

**Patterns:**
- `register_error_handlers(app)` in `backend/app/infrastructure/http/error_handlers.py` registers `400`, `404`, `405`, `429`, `500`, and a catch-all `Exception` handler returning JSON with optional `code` field.
- Item creation validation returns `422` with `{"error": "Field 'name' is required"}` from the controller without using those global handlers for that path.

## Cross-Cutting Concerns

**Logging:** `configure_logging` in `backend/app/logging_config.py` — structlog with JSON or console renderer; `logging.basicConfig` for stdlib loggers. Chosen in `create_app` from `LOG_FORMAT` / `DEBUG`.

**Validation:** Request parsing in routes (`items.py`); minimal validation in `ItemController.create_item` (non-empty `name`). No shared validation framework in domain layer.

**Authentication:** Not implemented in template; endpoints are open.

---

*Architecture analysis: 2026-03-28*

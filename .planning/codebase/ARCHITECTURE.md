# Architecture

**Analysis Date:** 2026-03-28

## Pattern Overview

**Overall:** Clean Architecture with Domain-Driven Design (DDD) layering and explicit dependency inversion.

**Key Characteristics:**

- **Dependency rule:** `infrastructure` → `application` → `domain`. The domain has no imports from Flask, SQLite, or HTTP.
- **Ports and adapters:** Persistence is abstracted behind `ItemRepository` (`typing.Protocol`); SQLite is one adapter wired in the application factory.
- **Application factory:** A single `create_app()` composes config, DB connection, repositories, use cases, controller, limiter, error handlers, and blueprints.

## Layers

**Domain:**

- Purpose: Core business concepts and invariants without framework or I/O.
- Location: `backend/app/domain/`
- Contains: Frozen dataclass entities (e.g. `Item`).
- Depends on: Standard library only (e.g. `dataclasses`).
- Used by: Application layer (use cases, DTOs that map from entities) and infrastructure (repository implementations that construct entities).

**Application:**

- Purpose: Use cases and contracts (ports, DTOs) that orchestrate domain logic and persistence.
- Location: `backend/app/application/`
- Contains: `ports/` (Protocols), `use_cases/` (per bounded context, e.g. `items/`), `dto/` (request/response shapes).
- Depends on: `domain` only for entities and business rules expressed in use cases.
- Used by: Infrastructure controllers and tests (via fakes implementing ports).

**Infrastructure:**

- Purpose: HTTP (Flask), persistence (SQLite), and cross-cutting wiring that touches the outside world.
- Location: `backend/app/infrastructure/`
- Contains: `http/` (routes, controllers, error handlers), `persistence/sqlite/` (schema + repository).
- Depends on: `application` (use cases, DTOs, ports) and `domain` (entities in adapters).
- Used by: `create_app()` in `backend/app/__init__.py`, which is the composition root.

## Data Flow

**HTTP request (example: `POST /api/v1/items`):**

1. Flask matches the route in `backend/app/infrastructure/http/routes/items.py` (blueprint factory `create_items_blueprint`).
2. The route parses JSON into `CreateItemRequest` (or `None` / invalid) and calls `ItemController.create_item` in `backend/app/infrastructure/http/controllers/item_controller.py`.
3. The controller validates presence of a non-empty `name` (returns 422-style body if invalid), then invokes `CreateItemUseCase.execute` in `backend/app/application/use_cases/items/create_item.py`.
4. The use case builds a domain `Item` (`id=0` placeholder) and calls `ItemRepository.add` (implemented by `SQLiteItemRepository` in `backend/app/infrastructure/persistence/sqlite/item_repository.py`).
5. SQLite inserts a row, commits, and the repository returns `Item` with the generated `id`.
6. The controller maps the entity to `ItemResponse` and returns a `(dict, status)` tuple; the route wraps it with `jsonify`.

**HTTP request (example: `GET /api/v1/items`):**

1. Route → `ItemController.list_items` → `ListItemsUseCase.execute` → `ItemRepository.list` → rows mapped to `Item` entities → serialized via `ItemResponse.from_entity`.

**Health probes:**

- `GET /health` and `GET /ready` are defined in `backend/app/infrastructure/http/routes/health.py` and registered without the `/api/v1` prefix in `create_app()`.

**State Management:**

- No global mutable domain state. Per-request state lives in Flask’s request context. A single long-lived `sqlite3.Connection` is stored on the app as `app.extensions["db_connection"]` in `backend/app/__init__.py` (tests use `:memory:`).

## Key Abstractions

**`Item` (entity):**

- Purpose: Immutable aggregate root for the sample “items” feature.
- Examples: `backend/app/domain/entities/item.py`
- Pattern: `@dataclass(frozen=True)`.

**`ItemRepository` (port):**

- Purpose: Contract for listing and persisting items without exposing SQL.
- Examples: `backend/app/application/ports/item_repository.py`
- Pattern: `typing.Protocol` with `list()` and `add(item: Item) -> Item`.

**Use cases:**

- Purpose: Single-responsibility application services; constructor-injected repository.
- Examples: `backend/app/application/use_cases/items/create_item.py`, `list_items.py`
- Pattern: `execute(...)` entry method; no Flask imports.

**`ItemController`:**

- Purpose: Bridge between HTTP concerns and use cases; returns raw dicts and status codes for routes to jsonify.
- Examples: `backend/app/infrastructure/http/controllers/item_controller.py`
- Pattern: Tuple return `(body, status)`; uses `ItemResponse.from_entity` for serialization.

**Blueprint factories:**

- Purpose: Inject controller and limiter into routes without module-level globals.
- Examples: `create_items_blueprint` in `backend/app/infrastructure/http/routes/items.py`
- Pattern: Factory function returning a configured `Blueprint`.

## Entry Points

**WSGI / development server:**

- Location: `backend/app/main.py`
- Triggers: `python -m app.main` from `backend/`, or Gunicorn targeting `app.main:app`.
- Responsibilities: Call `create_app()` and expose module-level `app`; optional `app.run()` for local dev.

**Application factory:**

- Location: `backend/app/__init__.py` (`create_app`)
- Triggers: `main.py`, pytest fixtures in `backend/tests/conftest.py` with `create_app({"TESTING": True, ...})`.
- Responsibilities: Load config via `backend/app/config.py`, configure structlog in `backend/app/logging_config.py`, open SQLite (or `:memory:` when testing), run `init_schema`, wire repository → use cases → controller → blueprints, attach limiter to `app.extensions["limiter"]`.

## Error Handling

**Strategy:** Global Flask error handlers plus controller-level validation for domain-specific input (e.g. missing item name).

**Patterns:**

- `register_error_handlers(app)` in `backend/app/infrastructure/http/error_handlers.py` returns JSON with `error` and optional `code` for 400, 404, 405, 429, 500, and a catch-all `Exception` handler that logs with `app.logger.exception`.
- `ItemController.create_item` returns `422` with a small error dict for invalid body; this is not necessarily aligned with the global `code` field pattern (document for future consistency if desired).

## Cross-Cutting Concerns

**Logging:** `configure_logging()` in `backend/app/logging_config.py` — structlog; JSON when `LOG_FORMAT=json` or non-debug production-style config (see `create_app`).

**Validation:** Light validation at the route (JSON shape → `CreateItemRequest`) and controller (non-empty `name`); no separate validation framework in the template.

**Authentication:** Not implemented; all sample endpoints are open.

**Rate limiting:** `flask_limiter.Limiter` in `create_app()`; per-route limits on items blueprint in `backend/app/infrastructure/http/routes/items.py`; disabled when `TESTING` is true. Strong reference kept via `app.extensions["limiter"]` to avoid GC issues with decorators.

**Schema initialization:** `init_schema` in `backend/app/infrastructure/persistence/sqlite/schema.py` — idempotent `CREATE TABLE IF NOT EXISTS`; also invoked from `SQLiteItemRepository.__init__` for safety.

---

*Architecture analysis: 2026-03-28*

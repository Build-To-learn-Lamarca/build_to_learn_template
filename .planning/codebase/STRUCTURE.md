# Codebase Structure

**Analysis Date:** 2026-03-28

## Directory Layout

```
build_to_learn_template/
├── backend/
│   ├── app/                          # Python package: Flask app + Clean Architecture layers
│   │   ├── __init__.py               # create_app() — composition root
│   │   ├── main.py                   # Gunicorn / python -m entry; exposes `app`
│   │   ├── config.py                 # get_config() from env + overrides
│   │   ├── logging_config.py         # structlog setup
│   │   ├── domain/
│   │   │   └── entities/             # e.g. item.py (Item)
│   │   ├── application/
│   │   │   ├── ports/                # Protocols (item_repository.py)
│   │   │   ├── use_cases/            # Subpackages per domain: items/
│   │   │   ├── dto/                  # CreateItemRequest, ItemResponse
│   │   │   └── __init__.py           # Re-exports use cases
│   │   └── infrastructure/
│   │       ├── http/
│   │       │   ├── error_handlers.py
│   │       │   ├── controllers/      # item_controller.py
│   │       │   └── routes/           # health.py, items.py (+ __init__.py exports)
│   │       └── persistence/
│   │           └── sqlite/           # schema.py, item_repository.py
│   ├── migrations/                 # 001_initial.sql, README.md
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests/
│       ├── conftest.py               # sys.path, create_app fixture, client
│       ├── unit/                     # domain, application, infrastructure
│       └── integration/http/         # Route-level tests
├── .github/                          # workflows, dependabot, templates
├── scripts/                          # e.g. check_no_env_committed.py
├── .cursor/rules/                    # project-context.mdc
├── pyproject.toml                    # Black, isort, Ruff, mypy, pytest paths
├── package.json / jest.config.js     # Optional JS tooling (scripts/js)
├── .pre-commit-config.yaml
├── .env.example                      # Document env vars (do not commit .env)
├── CLAUDE.md
└── README.md
```

## Directory Purposes

**`backend/app/`:**

- Purpose: All production Python code for the API; import root is `app` when `backend` is on `PYTHONPATH` or cwd.
- Contains: Factory, config, domain, application, infrastructure.
- Key files: `backend/app/__init__.py`, `backend/app/main.py`.

**`backend/app/domain/entities/`:**

- Purpose: Pure domain models.
- Contains: One module per aggregate/entity in the template (`item.py`).
- Key files: `backend/app/domain/entities/item.py`.

**`backend/app/application/`:**

- Purpose: Ports, DTOs, and use cases — no Flask.
- Contains: `ports/item_repository.py`, `dto/item_dto.py`, `use_cases/items/*.py`.
- Key files: `backend/app/application/use_cases/__init__.py` (barrel for use cases).

**`backend/app/infrastructure/http/`:**

- Purpose: Adapters for HTTP: routing, controllers, global errors.
- Contains: Blueprints, `ItemController`, `register_error_handlers`.
- Key files: `backend/app/infrastructure/http/routes/items.py`, `health.py`.

**`backend/app/infrastructure/persistence/sqlite/`:**

- Purpose: SQLite adapter for `ItemRepository` and schema bootstrap.
- Contains: `schema.py`, `item_repository.py`.
- Key files: Same; mirrors optional SQL in `backend/migrations/001_initial.sql`.

**`backend/tests/`:**

- Purpose: pytest suites mirroring layer boundaries.
- Contains: `unit/domain`, `unit/application`, `unit/infrastructure`, `integration/http`.
- Key files: `backend/tests/conftest.py`.

**`backend/migrations/`:**

- Purpose: Reference SQL and documentation for evolving schema (Alembic path described in README there).
- Key files: `backend/migrations/README.md`, `001_initial.sql`.

## Key File Locations

**Entry Points:**

- `backend/app/main.py`: Runnable module and Gunicorn target `app.main:app`.
- `backend/app/__init__.py`: `create_app()` — wire everything.

**Configuration:**

- `backend/app/config.py`: Environment-driven dict for Flask and DB paths.
- `pyproject.toml`: Tooling and `pytest` `testpaths = ["backend/tests"]`.

**Core Logic:**

- Use cases: `backend/app/application/use_cases/items/create_item.py`, `list_items.py`.
- Persistence: `backend/app/infrastructure/persistence/sqlite/item_repository.py`.

**Testing:**

- Fixtures: `backend/tests/conftest.py`.
- HTTP integration: `backend/tests/integration/http/test_items.py`, `test_health.py`, `test_error_handlers.py`.

## Naming Conventions

**Files:**

- Python modules: `snake_case.py` (e.g. `item_repository.py`, `create_item.py`).
- Test files: `test_<area>.py` under `backend/tests/`.

**Directories:**

- Layer folders: lowercase `domain`, `application`, `infrastructure`.
- Feature subpackages under use cases: plural resource name `items/` matching REST resource.

**Symbols:**

- Classes: `PascalCase` (`Item`, `CreateItemUseCase`, `SQLiteItemRepository`).
- Functions and methods: `snake_case` (`create_app`, `execute`, `init_schema`).
- Flask blueprints: module-level `health_bp`; factory `create_items_blueprint` for injected resources.

## Where to Add New Code

**New REST resource (e.g. `widgets`):**

- Domain entity: `backend/app/domain/entities/widget.py`.
- Port: `backend/app/application/ports/widget_repository.py` (Protocol).
- DTOs: `backend/app/application/dto/widget_dto.py`.
- Use cases: `backend/app/application/use_cases/widgets/` with `__init__.py` exporting public classes; add exports to `backend/app/application/use_cases/__init__.py` if you want a single import surface.
- SQLite (if used): `backend/app/infrastructure/persistence/sqlite/widget_repository.py` and extend `schema.py` / migrations.
- HTTP: `backend/app/infrastructure/http/controllers/widget_controller.py`, `routes/widgets.py` with a `create_widgets_blueprint(...)` factory.
- Wiring: Instantiate repo, use cases, controller in `backend/app/__init__.py` and `register_blueprint` with the same URL prefix pattern as items (`/api/v1`).
- Tests: `backend/tests/unit/...` per layer; `backend/tests/integration/http/test_widgets.py`.

**Utilities:**

- Shared helpers that must stay framework-free: prefer `backend/app/application/` or a new `backend/app/domain/` submodule if they encode rules.
- Flask-specific helpers: `backend/app/infrastructure/http/` (avoid leaking into domain).

**Jobs / CLI (not in template):**

- Add a new package under `backend/` (e.g. `backend/worker/`) and import `create_app` or shared use cases from `app` — keep the same dependency direction.

## Special Directories

**`.planning/codebase/`:**

- Purpose: GSD / planner artifacts (this mapping). Not part of runtime.
- Generated: By mapping workflows.
- Committed: Team choice; documents are safe to commit if they contain no secrets.

**`backend/tests/conftest.py`:**

- Purpose: Inserts `backend` onto `sys.path` so `from app import create_app` works from repo root when running `pytest`.

---

*Structure analysis: 2026-03-28*

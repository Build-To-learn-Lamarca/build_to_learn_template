# Codebase Structure

**Analysis Date:** 2026-03-28

## Directory Layout

```
build_to_learn_template/
├── backend/
│   ├── app/                          # Python package root (import as `app`)
│   │   ├── __init__.py               # create_app factory, wiring
│   │   ├── main.py                   # WSGI entry: app = create_app()
│   │   ├── config.py                 # get_config() from env
│   │   ├── logging_config.py         # structlog setup
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── item.py
│   │   ├── application/
│   │   │   ├── ports/
│   │   │   │   └── item_repository.py
│   │   │   ├── dto/
│   │   │   │   └── item_dto.py
│   │   │   └── use_cases/
│   │   │       ├── items/
│   │   │       │   ├── create_item.py
│   │   │       │   └── list_items.py
│   │   │       └── __init__.py       # re-exports use cases
│   │   └── infrastructure/
│   │       ├── http/
│   │       │   ├── error_handlers.py
│   │       │   ├── controllers/
│   │       │   │   └── item_controller.py
│   │       │   └── routes/
│   │       │       ├── __init__.py   # health_bp, create_items_blueprint
│   │       │       ├── health.py
│   │       │       └── items.py
│   │       └── persistence/
│   │           └── sqlite/
│   │               ├── schema.py
│   │               └── item_repository.py
│   ├── migrations/
│   │   ├── 001_initial.sql           # Optional manual bootstrap
│   │   └── README.md                 # SQLite + Alembic notes
│   ├── tests/
│   │   ├── conftest.py               # app + client fixtures, sys.path
│   │   ├── unit/
│   │   │   ├── domain/entities/
│   │   │   ├── application/          # use_cases + fakes.py
│   │   │   └── infrastructure/persistence/
│   │   └── integration/http/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── scripts/
│   ├── check_no_env_committed.py
│   └── js/                           # Jest example assets
├── .github/
│   ├── workflows/                    # pr-checks.yml, build-publish.yml
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
├── .cursor/rules/
│   └── project-context.mdc
├── .planning/codebase/               # GSD mapper outputs (this folder)
├── pyproject.toml                    # Black, isort, Ruff, mypy, pytest
├── package.json                      # npm test → jest
├── jest.config.js
├── Dockerfile.template               # CI-generated Dockerfile source
├── docker-compose.template.yml       # Optional local compose (placeholders)
├── CLAUDE.md
├── README.md
└── .pre-commit-config.yaml
```

## Directory Purposes

**`backend/app/`:**

- Purpose: Installable-style application tree; all runtime Python for the API lives here.
- Contains: Domain, application, infrastructure packages and `create_app`.
- Key files: `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`.

**`backend/migrations/`:**

- Purpose: SQL and documentation for schema evolution; complements runtime `init_schema` in `backend/app/infrastructure/persistence/sqlite/schema.py`.
- Contains: `001_initial.sql`, `README.md`.

**`backend/tests/`:**

- Purpose: pytest suites mirroring layer structure (`unit` vs `integration/http`).
- Contains: `conftest.py`, `unit/`, `integration/http/`.

**`.github/workflows/`:**

- Purpose: CI — lint, test, SAST/DAST on PRs; image build and registry push on main.
- Contains: `pr-checks.yml`, `build-publish.yml`.

**`scripts/`:**

- Purpose: Repo maintenance and non-Python-tooling examples (e.g. Jest under `scripts/js/` per project docs).

## Key File Locations

**Entry Points:**

- `backend/app/main.py`: WSGI `app` for gunicorn and local run.
- `backend/app/__init__.py`: `create_app()` — single composition root.

**Configuration:**

- `backend/app/config.py`: `get_config()` reads `LOG_LEVEL`, `DEBUG`, `SECRET_KEY`, `SQLITE_PATH`, `DATABASE_URL`.
- `pyproject.toml`: tool configs for Black, isort, Ruff, mypy, pytest (`testpaths = backend/tests`, `files = backend/app` for mypy).

**Core Logic:**

- Domain: `backend/app/domain/entities/item.py`.
- Use cases: `backend/app/application/use_cases/items/*.py`.
- HTTP surface: `backend/app/infrastructure/http/routes/*.py`, `item_controller.py`.
- Persistence: `backend/app/infrastructure/persistence/sqlite/item_repository.py`, `schema.py`.

**Testing:**

- `backend/tests/conftest.py`: inserts `backend/` on `sys.path`, `create_app` with `TESTING=True`.
- Integration: `backend/tests/integration/http/test_health.py`, `test_items.py`, `test_error_handlers.py`.
- Unit examples: `backend/tests/unit/application/use_cases/`, `backend/tests/unit/domain/entities/`, `backend/tests/unit/infrastructure/persistence/`.

**Container:**

- `Dockerfile.template`: multi-stage build; copies `backend/app` to `/app/app`, runs gunicorn `app.main:app`.

## Naming Conventions

**Files:**

- Python modules: `snake_case.py` (e.g. `item_repository.py`, `create_item.py`).
- Test files: `test_*.py` under `backend/tests/` (pytest discovery).
- Workflow YAML: kebab or snake in filename (`pr-checks.yml`).

**Directories:**

- Layer folders: lowercase `domain`, `application`, `infrastructure`.
- Use-case grouping: `application/use_cases/<aggregate>/` (e.g. `items/`).

**Symbols:**

- Classes: `PascalCase` (`Item`, `CreateItemUseCase`, `SQLiteItemRepository`).
- Functions and variables: `snake_case` (`create_app`, `get_config`, `list_items`).

## Where to Add New Code

**New REST resource (mirror items):**

- Domain entity: `backend/app/domain/entities/<name>.py`.
- Port: `backend/app/application/ports/<name>_repository.py` (Protocol).
- DTOs: `backend/app/application/dto/<name>_dto.py`.
- Use cases: `backend/app/application/use_cases/<plural>/` (one module per operation).
- Re-export use cases from `backend/app/application/use_cases/__init__.py` if they should be imported from the package root.
- Repository impl: `backend/app/infrastructure/persistence/sqlite/` (or new subpackage for another DB).
- Controller: `backend/app/infrastructure/http/controllers/<name>_controller.py`.
- Routes: new module under `backend/app/infrastructure/http/routes/` with a `create_*_blueprint(controller, limiter)` factory; export from `routes/__init__.py`.
- Wiring: register blueprint and construct use cases/controller in `backend/app/__init__.py`.

**Tests:**

- Unit (domain/use case): `backend/tests/unit/...` matching layer path.
- HTTP integration: `backend/tests/integration/http/test_<feature>.py`.

**Schema:**

- SQL file in `backend/migrations/` for documentation/manual runs; update `init_schema` in `schema.py` if SQLite schema changes at startup.

**Utilities:**

- Cross-cutting helpers that must stay framework-free: prefer `backend/app/application/` or a small `backend/app/domain/` helper if purely domain rules.
- Flask-specific helpers: `backend/app/infrastructure/http/`.

## Special Directories

**`.planning/codebase/`:**

- Purpose: GSD codebase-mapper outputs (architecture, stack, testing, concerns).
- Generated: No — maintained by mapping workflow.
- Committed: Yes (typical for GSD projects).

**`backend/app/` (import name `app`):**

- Purpose: First-party package name used in imports (`from app.xxx import ...`).
- Note: `pyproject.toml` sets `known_first_party = ["app"]` and mypy `files = ["backend/app"]`; tests run with `backend` on path via `conftest.py`.

---

*Structure analysis: 2026-03-28*

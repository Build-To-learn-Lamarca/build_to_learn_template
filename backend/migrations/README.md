# Migrations

## SQLite (template default)

When using a **file-based SQLite** database (not `:memory:`), you can bootstrap the schema in two ways:

1. **Automatic**: The app creates tables on startup via `init_schema()` in `app.infrastructure.persistence.sqlite.schema`.
2. **Manual**: Run the SQL script once before starting the app:

   ```bash
   # From repo root, with SQLITE_PATH=data/app.db (create data/ first: mkdir data)
   sqlite3 data/app.db < backend/migrations/001_initial.sql
   ```

## PostgreSQL / other databases (Alembic)

When switching to PostgreSQL (or another DB) via `DATABASE_URL`, add [Alembic](https://alembic.sqlalchemy.org/) to the project:

1. `pip install alembic psycopg2-binary` (or your driver).
2. `alembic init alembic` in the backend.
3. Point `alembic.ini` and `env.py` at your connection string (e.g. from `DATABASE_URL`).
4. Add a revision that creates the `items` table (or import from `001_initial.sql` and adapt SQL dialect).
5. Run `alembic upgrade head` before starting the app.

The template keeps a single SQLite migration file so new repos can run it or mirror it in Alembic when they add a second database.

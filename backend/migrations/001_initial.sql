-- Initial schema for SQLite (run when moving off :memory: or bootstrapping a new DB file).
-- Usage: sqlite3 data/app.db < backend/migrations/001_initial.sql
-- Or from repo root: sqlite3 backend/../data/app.db < backend/migrations/001_initial.sql

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

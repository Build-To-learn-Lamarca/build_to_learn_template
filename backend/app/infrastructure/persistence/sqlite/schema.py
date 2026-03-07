"""SQLite schema — create tables. Run on first use or via init."""

from __future__ import annotations

import sqlite3


def init_schema(conn: sqlite3.Connection) -> None:
    """Create tables required by the application."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )
    conn.commit()

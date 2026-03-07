"""Application configuration — env and defaults."""

from __future__ import annotations

import os


def get_config(config_override: dict[str, object] | None = None) -> dict[str, object]:
    """Build config from env and optional override (e.g. TESTING)."""
    default_sqlite = os.getenv("SQLITE_PATH", "data/app.db")
    config: dict[str, object] = {
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-change-in-production"),
        "SQLITE_PATH": default_sqlite,
        "DATABASE_URL": os.getenv("DATABASE_URL", "").strip(),
    }
    if config_override:
        config.update(config_override)
    return config

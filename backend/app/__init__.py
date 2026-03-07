"""Application factory — Clean Architecture wiring."""

from __future__ import annotations

import os
import sqlite3

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import get_config
from app.logging_config import configure_logging
from app.infrastructure.http.error_handlers import register_error_handlers
from app.infrastructure.http.routes import create_items_blueprint, health_bp
from app.infrastructure.persistence.sqlite import SQLiteItemRepository, init_schema
from app.application.use_cases import CreateItemUseCase, ListItemsUseCase
from app.infrastructure.http.controllers.item_controller import ItemController


def create_app(config: dict[str, object] | None = None) -> Flask:
    """Create and configure the Flask application with wired dependencies."""
    app = Flask(__name__)
    cfg = get_config(config)

    app.config.from_mapping(cfg)

    # Logging: structlog with JSON in production (observability), console in dev
    json_logs = os.getenv("LOG_FORMAT", "").lower() == "json" or not cfg.get("DEBUG")
    configure_logging(
        log_level=str(cfg.get("LOG_LEVEL", "INFO")),
        json_logs=json_logs,
        debug=bool(cfg.get("DEBUG")),
    )

    # Database: SQLite (dev/test). Use DATABASE_URL for other adapters in production.
    db_path = ":memory:" if cfg.get("TESTING") else str(cfg["SQLITE_PATH"])
    if db_path != ":memory:":
        dirpath = os.path.dirname(db_path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    app.extensions["db_connection"] = conn

    # Repository and use cases
    item_repo = SQLiteItemRepository(conn)
    list_items_uc = ListItemsUseCase(item_repo)
    create_item_uc = CreateItemUseCase(item_repo)
    item_controller = ItemController(list_items_uc, create_item_uc)

    # Rate limiting (disabled in TESTING)
    app.config.setdefault("RATELIMIT_ENABLED", not cfg.get("TESTING"))
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day"],
        storage_uri="memory://",
    )
    limiter.init_app(app)
    app.extensions["limiter"] = limiter  # keep strong reference for blueprint decorators

    # Global error handlers (JSON responses for 400, 404, 405, 500)
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(
        create_items_blueprint(item_controller, limiter), url_prefix="/api/v1"
    )

    return app

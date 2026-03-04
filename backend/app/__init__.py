"""Application factory for the api-container template."""

from __future__ import annotations

import logging
import os

from flask import Flask

from app.routes.health import health_bp
from app.routes.example import example_bp


def create_app(config: dict[str, object] | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ── Default configuration ───────────────────────────────────────────────
    app.config.from_mapping(
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        DEBUG=os.getenv("DEBUG", "false").lower() == "true",
    )

    if config:
        app.config.update(config)

    # ── Logging ────────────────────────────────────────────────────────────
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ── Blueprints ─────────────────────────────────────────────────────────
    app.register_blueprint(health_bp)
    app.register_blueprint(example_bp, url_prefix="/api/v1")

    return app

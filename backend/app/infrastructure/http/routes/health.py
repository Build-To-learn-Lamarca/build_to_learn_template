"""Health check routes — liveness and readiness."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask.wrappers import Response

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Liveness probe — returns 200 when the app is running."""
    return jsonify({"status": "ok"}), 200


@health_bp.route("/ready", methods=["GET"])
def ready() -> tuple[Response, int]:
    """Readiness probe — extend to check DB/deps connectivity."""
    return jsonify({"status": "ready"}), 200

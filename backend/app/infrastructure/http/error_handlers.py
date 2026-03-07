"""Global Flask error handlers — standardized JSON responses."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, request


def _error_response(message: str, status_code: int, code: str | None = None) -> tuple[dict[str, Any], int]:
    """Build consistent JSON error body and status."""
    body: dict[str, Any] = {"error": message}
    if code:
        body["code"] = code
    return body, status_code


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for 400, 404, 500 and unhandled exceptions."""

    @app.errorhandler(400)
    def bad_request(e: Exception) -> tuple:
        return jsonify(_error_response("Bad Request", 400, "BAD_REQUEST")[0]), 400

    @app.errorhandler(404)
    def not_found(e: Exception) -> tuple:
        return jsonify(_error_response("Not Found", 404, "NOT_FOUND")[0]), 404

    @app.errorhandler(405)
    def method_not_allowed(e: Exception) -> tuple:
        return jsonify(_error_response("Method Not Allowed", 405, "METHOD_NOT_ALLOWED")[0]), 405

    @app.errorhandler(429)
    def too_many_requests(e: Exception) -> tuple:
        return jsonify(_error_response("Too Many Requests", 429, "RATE_LIMIT_EXCEEDED")[0]), 429

    @app.errorhandler(500)
    def internal_error(e: Exception) -> tuple:
        app.logger.exception("Unhandled error: %s", e)
        return jsonify(_error_response("Internal Server Error", 500, "INTERNAL_ERROR")[0]), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e: Exception) -> tuple:
        app.logger.exception("Unhandled exception: %s", e)
        return jsonify(_error_response("Internal Server Error", 500, "INTERNAL_ERROR")[0]), 500

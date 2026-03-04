"""Tests for health check endpoints.

Covers: liveness (/health) and readiness (/ready) probes.
"""

from __future__ import annotations

from flask.testing import FlaskClient


class TestHealthEndpoint:
    """Liveness probe — GET /health."""

    def test_returns_200(self, client: FlaskClient) -> None:
        """Liveness probe must return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_json_status_ok(self, client: FlaskClient) -> None:
        """Liveness probe body must be {"status": "ok"}."""
        response = client.get("/health")
        data = response.get_json()
        assert data == {"status": "ok"}

    def test_content_type_is_json(self, client: FlaskClient) -> None:
        """Liveness probe must return application/json content type."""
        response = client.get("/health")
        assert response.content_type == "application/json"


class TestReadyEndpoint:
    """Readiness probe — GET /ready."""

    def test_returns_200(self, client: FlaskClient) -> None:
        """Readiness probe must return HTTP 200."""
        response = client.get("/ready")
        assert response.status_code == 200

    def test_returns_json_status_ready(self, client: FlaskClient) -> None:
        """Readiness probe body must be {"status": "ready"}."""
        response = client.get("/ready")
        data = response.get_json()
        assert data == {"status": "ready"}

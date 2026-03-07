"""Integration tests for health check endpoints."""

from __future__ import annotations

from flask.testing import FlaskClient


class TestHealthEndpoint:
    """Liveness probe — GET /health."""

    def test_returns_200(self, client: FlaskClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_json_status_ok(self, client: FlaskClient) -> None:
        response = client.get("/health")
        data = response.get_json()
        assert data == {"status": "ok"}

    def test_content_type_is_json(self, client: FlaskClient) -> None:
        response = client.get("/health")
        assert response.content_type == "application/json"


class TestReadyEndpoint:
    """Readiness probe — GET /ready."""

    def test_returns_200(self, client: FlaskClient) -> None:
        response = client.get("/ready")
        assert response.status_code == 200

    def test_returns_json_status_ready(self, client: FlaskClient) -> None:
        response = client.get("/ready")
        data = response.get_json()
        assert data == {"status": "ready"}

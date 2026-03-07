"""Integration tests for global error handlers (404, 400, 500)."""

from __future__ import annotations

from flask.testing import FlaskClient


class TestNotFoundHandler:
    """GET unknown path returns 404 JSON."""

    def test_404_returns_json(self, client: FlaskClient) -> None:
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        data = response.get_json()
        assert data is not None
        assert "error" in data
        assert data.get("code") == "NOT_FOUND"

    def test_404_message(self, client: FlaskClient) -> None:
        response = client.get("/unknown")
        assert response.status_code == 404
        assert response.get_json()["error"] == "Not Found"


class TestMethodNotAllowedHandler:
    """Method not allowed returns 405 JSON."""

    def test_405_returns_json(self, client: FlaskClient) -> None:
        response = client.put("/health")
        assert response.status_code == 405
        data = response.get_json()
        assert data is not None
        assert data.get("code") == "METHOD_NOT_ALLOWED"
        assert "error" in data

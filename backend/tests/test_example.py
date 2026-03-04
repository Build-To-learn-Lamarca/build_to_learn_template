"""Tests for the example resource blueprint (GET /api/v1/items, POST /api/v1/items).

Replace with tests for your actual domain resource.
"""

from __future__ import annotations

from flask.testing import FlaskClient


class TestListItems:
    """GET /api/v1/items — list all items."""

    def test_empty_list_on_fresh_app(self, client: FlaskClient) -> None:
        """A fresh app should return an empty list."""
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_200(self, client: FlaskClient) -> None:
        response = client.get("/api/v1/items")
        assert response.status_code == 200


class TestCreateItem:
    """POST /api/v1/items — create a new item."""

    def test_creates_item_returns_201(self, client: FlaskClient) -> None:
        """Valid body must return 201 and the created item."""
        response = client.post("/api/v1/items", json={"name": "Widget"})
        assert response.status_code == 201

    def test_created_item_has_name_and_id(self, client: FlaskClient) -> None:
        """Response body must include 'name' and 'id' fields."""
        response = client.post("/api/v1/items", json={"name": "Gadget"})
        data = response.get_json()
        assert "id" in data
        assert data["name"] == "Gadget"

    def test_missing_name_returns_422(self, client: FlaskClient) -> None:
        """Missing 'name' field must return 422 Unprocessable Entity."""
        response = client.post("/api/v1/items", json={"other": "value"})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client: FlaskClient) -> None:
        """Empty body (no JSON) must return 422."""
        response = client.post(
            "/api/v1/items",
            data="",
            content_type="application/json",
        )
        assert response.status_code == 422

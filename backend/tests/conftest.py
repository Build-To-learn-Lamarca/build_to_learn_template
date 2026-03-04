"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture()
def app() -> object:
    """Create application instance configured for testing."""
    test_app = create_app({"TESTING": True, "DEBUG": False})
    yield test_app


@pytest.fixture()
def client(app: object) -> FlaskClient:
    """Return a test client for the app."""
    return app.test_client()  # type: ignore[union-attr]

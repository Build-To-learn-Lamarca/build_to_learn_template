"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from flask.testing import FlaskClient

# Ensure backend is on path so "app" and "tests" resolve when run from repo root
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

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

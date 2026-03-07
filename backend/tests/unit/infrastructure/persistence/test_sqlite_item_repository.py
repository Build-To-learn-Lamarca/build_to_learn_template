"""Unit tests for SQLiteItemRepository (in-memory DB)."""

from __future__ import annotations

import sqlite3

import pytest

from app.domain.entities.item import Item
from app.infrastructure.persistence.sqlite.item_repository import SQLiteItemRepository


@pytest.fixture
def sqlite_repo() -> SQLiteItemRepository:
    """Repository backed by in-memory SQLite."""
    conn = sqlite3.connect(":memory:")
    return SQLiteItemRepository(conn)


class TestSQLiteItemRepository:
    """SQLiteItemRepository list and add."""

    def test_list_empty(self, sqlite_repo: SQLiteItemRepository) -> None:
        assert sqlite_repo.list() == []

    def test_add_returns_item_with_id(self, sqlite_repo: SQLiteItemRepository) -> None:
        added = sqlite_repo.add(Item(id=0, name="Widget"))
        assert added.id != 0
        assert added.name == "Widget"

    def test_add_and_list(self, sqlite_repo: SQLiteItemRepository) -> None:
        sqlite_repo.add(Item(id=0, name="A"))
        sqlite_repo.add(Item(id=0, name="B"))
        items = sqlite_repo.list()
        assert len(items) == 2
        assert items[0].name == "A" and items[1].name == "B"

"""Fake implementations for application layer tests."""

from __future__ import annotations

from app.domain.entities.item import Item


class InMemoryItemRepository:
    """In-memory implementation of ItemRepository for tests."""

    def __init__(self) -> None:
        self._items: list[Item] = []
        self._next_id = 1

    def list(self) -> list[Item]:
        return list(self._items)

    def add(self, item: Item) -> Item:
        new_id = self._next_id
        self._next_id += 1
        new_item = Item(id=new_id, name=item.name)
        self._items.append(new_item)
        return new_item


class FailingItemRepository:
    """ItemRepository that raises on every call — for failure path tests."""

    def list(self) -> list[Item]:
        raise RuntimeError("repository list failed")

    def add(self, item: Item) -> Item:
        raise RuntimeError("repository add failed")

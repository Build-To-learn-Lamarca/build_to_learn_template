"""Port: repository for Item aggregate."""

from __future__ import annotations

from typing import Protocol

from app.domain.entities.item import Item


class ItemRepository(Protocol):
    """Interface for Item persistence. Implement in infrastructure."""

    def list(self) -> list[Item]:
        """Return all items."""
        pass

    def add(self, item: Item) -> Item:
        """Persist item and return it (e.g. with generated id)."""
        pass

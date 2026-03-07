"""List all items use case."""

from __future__ import annotations

from app.application.ports.item_repository import ItemRepository
from app.domain.entities.item import Item


class ListItemsUseCase:
    """Returns all items from the repository."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Item]:
        """Return all items."""
        return self._repository.list()

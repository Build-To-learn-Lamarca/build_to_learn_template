"""Create item use case."""

from __future__ import annotations

from app.application.dto.item_dto import CreateItemRequest
from app.application.ports.item_repository import ItemRepository
from app.domain.entities.item import Item


class CreateItemUseCase:
    """Creates an item and persists it via the repository."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def execute(self, request: CreateItemRequest) -> Item:
        """Create and persist item; return entity with assigned id."""
        item = Item(id=0, name=request.name)
        return self._repository.add(item)

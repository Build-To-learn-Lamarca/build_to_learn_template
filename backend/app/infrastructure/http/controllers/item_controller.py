"""Controller for Item resource — delegates to use cases, returns (body, status)."""

from __future__ import annotations

from typing import Any

from app.application.dto.item_dto import CreateItemRequest, ItemResponse
from app.application.use_cases import CreateItemUseCase, ListItemsUseCase


class ItemController:
    """Handles HTTP-level input/output for items; calls use cases."""

    def __init__(
        self,
        list_items_use_case: ListItemsUseCase,
        create_item_use_case: CreateItemUseCase,
    ) -> None:
        self._list_items = list_items_use_case
        self._create_item = create_item_use_case

    def list_items(self) -> tuple[list[dict[str, Any]], int]:
        """Return all items as list of dicts and 200."""
        items = self._list_items.execute()
        body = [ItemResponse.from_entity(i).__dict__ for i in items]
        return body, 200

    def create_item(
        self, request: CreateItemRequest | None
    ) -> tuple[dict[str, Any], int]:
        """Create item. Returns (item_dict, 201) or (error_dict, 422)."""
        if request is None or not request.name.strip():
            return ({"error": "Field 'name' is required"}, 422)
        item = self._create_item.execute(request)
        body = ItemResponse.from_entity(item).__dict__
        return body, 201

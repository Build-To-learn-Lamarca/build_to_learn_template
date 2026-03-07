"""DTOs for Item resource."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateItemRequest:
    """Request to create an item."""

    name: str


@dataclass(frozen=True)
class ItemResponse:
    """Response model for a single item."""

    id: int
    name: str

    @classmethod
    def from_entity(cls, item: object) -> ItemResponse:
        """Build from domain entity (Item)."""
        from app.domain.entities.item import Item

        if not isinstance(item, Item):
            raise TypeError("item must be Item")
        return cls(id=item.id, name=item.name)

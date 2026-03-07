"""Unit tests for domain entity Item."""

from __future__ import annotations

from app.domain.entities.item import Item


class TestItem:
    """Item entity — id and name."""

    def test_item_has_id_and_name(self) -> None:
        """Item must have id and name attributes."""
        item = Item(id=1, name="Widget")
        assert item.id == 1
        assert item.name == "Widget"

    def test_item_equality_by_id_and_name(self) -> None:
        """Two items with same id and name are equal."""
        a = Item(id=1, name="X")
        b = Item(id=1, name="X")
        assert a == b

    def test_item_inequality_when_different(self) -> None:
        """Items with different id or name are not equal."""
        a = Item(id=1, name="X")
        assert a != Item(id=2, name="X")
        assert a != Item(id=1, name="Y")

    def test_item_is_not_equal_to_non_item(self) -> None:
        """Item must not compare equal to non-Item."""
        item = Item(id=1, name="X")
        assert item != 1
        assert item != {"id": 1, "name": "X"}

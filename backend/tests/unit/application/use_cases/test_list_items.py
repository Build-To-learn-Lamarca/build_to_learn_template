"""Unit tests for ListItemsUseCase."""

from __future__ import annotations

import pytest

from app.application.use_cases import ListItemsUseCase
from app.domain.entities.item import Item
from tests.unit.application.fakes import FailingItemRepository, InMemoryItemRepository


class TestListItemsUseCase:
    """ListItemsUseCase returns all items from repository."""

    def test_returns_empty_list_when_no_items(self) -> None:
        """Repository with no items returns empty list."""
        repo = InMemoryItemRepository()
        use_case = ListItemsUseCase(repo)
        result = use_case.execute()
        assert result == []

    def test_returns_all_items_from_repository(self) -> None:
        """All persisted items are returned."""
        repo = InMemoryItemRepository()
        repo.add(Item(id=1, name="A"))
        repo.add(Item(id=2, name="B"))
        use_case = ListItemsUseCase(repo)
        result = use_case.execute()
        assert len(result) == 2
        assert result[0].id == 1 and result[0].name == "A"
        assert result[1].id == 2 and result[1].name == "B"

    def test_propagates_repository_exception_on_list(self) -> None:
        """When repository.list() raises, use case propagates the exception."""
        repo = FailingItemRepository()
        use_case = ListItemsUseCase(repo)
        with pytest.raises(RuntimeError, match="repository list failed"):
            use_case.execute()

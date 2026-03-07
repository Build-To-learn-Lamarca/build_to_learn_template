"""Unit tests for CreateItemUseCase."""

from __future__ import annotations

import pytest

from app.application.dto.item_dto import CreateItemRequest
from app.application.use_cases import CreateItemUseCase
from tests.unit.application.fakes import FailingItemRepository, InMemoryItemRepository


class TestCreateItemUseCase:
    """CreateItemUseCase persists item and returns it."""

    def test_creates_item_with_auto_id(self) -> None:
        """First item gets id 1, second gets id 2."""
        repo = InMemoryItemRepository()
        use_case = CreateItemUseCase(repo)
        req = CreateItemRequest(name="Widget")
        result = use_case.execute(req)
        assert result.id == 1
        assert result.name == "Widget"

    def test_persists_item_in_repository(self) -> None:
        """Created item is stored and listed."""
        repo = InMemoryItemRepository()
        use_case = CreateItemUseCase(repo)
        use_case.execute(CreateItemRequest(name="A"))
        use_case.execute(CreateItemRequest(name="B"))
        all_items = repo.list()
        assert len(all_items) == 2
        assert all_items[0].name == "A" and all_items[1].name == "B"

    def test_propagates_repository_exception_on_add(self) -> None:
        """When repository.add() raises, use case propagates the exception."""
        repo = FailingItemRepository()
        use_case = CreateItemUseCase(repo)
        with pytest.raises(RuntimeError, match="repository add failed"):
            use_case.execute(CreateItemRequest(name="X"))

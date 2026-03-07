"""Domain entity Item."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """Item entity with identity and name."""

    id: int
    name: str

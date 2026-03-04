"""Example resource blueprint.

Replace this with the actual domain resource of your service.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

example_bp = Blueprint("example", __name__)

# In-memory store — replace with a real database layer.
_items: list[dict[str, object]] = []


@example_bp.get("/items")
def list_items() -> tuple[Response, int]:
    """Return all items."""
    return jsonify(_items), 200


@example_bp.post("/items")
def create_item() -> tuple[Response, int]:
    """Create a new item.

    Expected JSON body: ``{"name": "string"}``
    """
    body = request.get_json(silent=True)
    if not body or "name" not in body:
        return jsonify({"error": "Field 'name' is required"}), 422

    item: dict[str, object] = {"id": len(_items) + 1, "name": body["name"]}
    _items.append(item)
    return jsonify(item), 201

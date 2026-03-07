"""Items API routes — parse request, call controller, return response."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter

from app.application.dto.item_dto import CreateItemRequest
from app.infrastructure.http.controllers.item_controller import ItemController


def create_items_blueprint(controller: ItemController, limiter: Limiter) -> Blueprint:
    """Create items blueprint with injected controller and rate limiter."""
    bp = Blueprint("items", __name__)

    @bp.route("/items", methods=["GET"])
    @limiter.limit("60 per minute")
    def list_items() -> tuple:
        body, status = controller.list_items()
        return jsonify(body), status

    @bp.route("/items", methods=["POST"])
    @limiter.limit("30 per minute")
    def create_item() -> tuple:
        raw = request.get_json(silent=True)
        req: CreateItemRequest | None = None
        if raw and isinstance(raw.get("name"), str):
            req = CreateItemRequest(name=raw["name"].strip())
        elif raw and "name" in raw:
            req = CreateItemRequest(name=str(raw["name"]).strip())
        body, status = controller.create_item(req)
        return jsonify(body), status

    return bp

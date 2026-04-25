"""Public (student-facing) endpoints that serve tenant-resolved data."""

from flask import Blueprint, g, jsonify

from database import db
from models.ui_config import UIConfig
from models.library_map import LibraryMap, BookLocation
from models.book import Book

public_bp = Blueprint("public", __name__, url_prefix="/api")


@public_bp.route("/config", methods=["GET"])
def get_tenant_config():
    """Return UI configuration for the current tenant (resolved by middleware)."""
    tenant = getattr(g, "tenant", None)
    if not tenant:
        return jsonify({"error": "Tenant could not be resolved"}), 400

    config = UIConfig.query.filter_by(tenant=tenant).first()
    if not config:
        return jsonify({"error": "No configuration for this tenant"}), 404

    return jsonify(config.to_dict()), 200


@public_bp.route("/map", methods=["GET"])
def get_tenant_map():
    """Return the library map for the current tenant."""
    tenant = getattr(g, "tenant", None)
    if not tenant:
        return jsonify({"error": "Tenant could not be resolved"}), 400

    lib_map = LibraryMap.query.filter_by(tenant=tenant).first()
    if not lib_map:
        return jsonify({"error": "Map not found"}), 404

    return jsonify(lib_map.to_dict()), 200


@public_bp.route("/map/book/<int:book_id>", methods=["GET"])
def get_book_location(book_id: int):
    """Return a specific book's location on the map."""
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if not book.location:
        return jsonify({"error": "No location set for this book"}), 404

    tenant = getattr(g, "tenant", None)
    lib_map = LibraryMap.query.filter_by(tenant=tenant).first() if tenant else None

    return jsonify({
        "book": {"id": book.id, "title": book.title},
        "location": book.location.to_dict(),
        "map": lib_map.to_dict() if lib_map else None,
    }), 200

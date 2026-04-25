"""CRUD endpoints for library maps and book locations."""

from flask import Blueprint, jsonify, request

from database import db
from models.library_map import LibraryMap, BookLocation

maps_bp = Blueprint("maps", __name__, url_prefix="/admin/maps")


@maps_bp.route("", methods=["GET"])
def get_map():
    """Get the library map for a tenant.

    Query params:
        tenant (str): required
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    lib_map = LibraryMap.query.filter_by(tenant=tenant).first()
    if not lib_map:
        return jsonify({"error": "Map not found for this tenant"}), 404

    return jsonify(lib_map.to_dict()), 200


@maps_bp.route("", methods=["POST"])
def create_or_update_map():
    """Upload / update the library map for a tenant.

    JSON body:
        tenant (str): required
        image_url (str): required
        width (int): optional
        height (int): optional
    """
    data = request.get_json(silent=True) or {}

    tenant = data.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant is required"}), 400
    image_url = data.get("image_url", "").strip()
    if not image_url:
        return jsonify({"error": "image_url is required"}), 400

    lib_map = LibraryMap.query.filter_by(tenant=tenant).first()

    if lib_map:
        lib_map.image_url = image_url
        lib_map.width = data.get("width")
        lib_map.height = data.get("height")
        status = 200
    else:
        lib_map = LibraryMap(
            tenant=tenant,
            image_url=image_url,
            width=data.get("width"),
            height=data.get("height"),
        )
        db.session.add(lib_map)
        status = 201

    db.session.commit()
    return jsonify(lib_map.to_dict()), status


@maps_bp.route("", methods=["DELETE"])
def delete_map():
    """Delete the library map for a tenant.

    Query params:
        tenant (str): required
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    lib_map = LibraryMap.query.filter_by(tenant=tenant).first()
    if not lib_map:
        return jsonify({"error": "Map not found for this tenant"}), 404

    db.session.delete(lib_map)
    db.session.commit()
    return jsonify({"message": "Map deleted"}), 200


@maps_bp.route("/locations", methods=["GET"])
def list_locations():
    """List all book locations for a tenant.

    Query params:
        tenant (str): required
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    locations = (
        db.session.query(BookLocation)
        .join(BookLocation.book)
        .filter_by(tenant=tenant)
        .all()
    )
    return jsonify([loc.to_dict() for loc in locations]), 200


@maps_bp.route("/locations/<int:location_id>", methods=["PUT"])
def update_location(location_id: int):
    """Update a specific book location on the map."""
    loc = db.session.get(BookLocation, location_id)
    if not loc:
        return jsonify({"error": "Location not found"}), 404

    data = request.get_json(silent=True) or {}
    for attr in ("x", "y", "label", "floor"):
        if attr in data:
            setattr(loc, attr, data[attr])

    db.session.commit()
    return jsonify(loc.to_dict()), 200

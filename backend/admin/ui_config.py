"""CRUD endpoints for per-tenant UI configuration."""

from flask import Blueprint, jsonify, request

from database import db
from models.ui_config import UIConfig

ui_config_bp = Blueprint("ui_config", __name__, url_prefix="/admin/ui-config")


@ui_config_bp.route("", methods=["GET"])
def get_config():
    """Get UI configuration for a tenant.

    Query params:
        tenant (str): required
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    config = UIConfig.query.filter_by(tenant=tenant).first()
    if not config:
        return jsonify({"error": "UI config not found for this tenant"}), 404

    return jsonify(config.to_dict()), 200


@ui_config_bp.route("", methods=["POST"])
def create_config():
    """Create UI configuration for a new tenant.

    JSON body:
        tenant (str): required
        university_name (str): required
        logo_url (str): optional
        primary_color (str): optional (hex, e.g. "#1a73e8")
        secondary_color (str): optional (hex)
        custom_labels (dict): optional
    """
    data = request.get_json(silent=True) or {}

    tenant = (data.get("tenant") or "").strip()
    if not tenant:
        return jsonify({"error": "tenant is required"}), 400

    university_name = (data.get("university_name") or "").strip()
    if not university_name:
        return jsonify({"error": "university_name is required"}), 400

    existing = UIConfig.query.filter_by(tenant=tenant).first()
    if existing:
        return jsonify({"error": "UI config already exists for this tenant; use PUT to update"}), 409

    config = UIConfig(
        tenant=tenant,
        university_name=university_name,
        logo_url=data.get("logo_url"),
        primary_color=data.get("primary_color", "#1a73e8"),
        secondary_color=data.get("secondary_color", "#ffffff"),
    )
    config.custom_labels = data.get("custom_labels")

    db.session.add(config)
    db.session.commit()
    return jsonify(config.to_dict()), 201


@ui_config_bp.route("", methods=["PUT"])
def update_config():
    """Update UI configuration for a tenant.

    Query params:
        tenant (str): required

    JSON body — all fields optional:
        university_name, logo_url, primary_color, secondary_color, custom_labels
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    config = UIConfig.query.filter_by(tenant=tenant).first()
    if not config:
        return jsonify({"error": "UI config not found for this tenant"}), 404

    data = request.get_json(silent=True) or {}

    for field in ("university_name", "logo_url", "primary_color", "secondary_color"):
        if field in data:
            setattr(config, field, data[field])

    if "custom_labels" in data:
        config.custom_labels = data["custom_labels"]

    db.session.commit()
    return jsonify(config.to_dict()), 200


@ui_config_bp.route("", methods=["DELETE"])
def delete_config():
    """Delete UI configuration for a tenant.

    Query params:
        tenant (str): required
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    config = UIConfig.query.filter_by(tenant=tenant).first()
    if not config:
        return jsonify({"error": "UI config not found for this tenant"}), 404

    db.session.delete(config)
    db.session.commit()
    return jsonify({"message": "UI config deleted"}), 200

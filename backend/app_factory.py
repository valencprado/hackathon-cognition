"""Application factory for the Flask backend.

Usage::

    from app_factory import create_app
    app = create_app()
"""

from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS

from database import db
from admin.books import books_bp
from admin.maps import maps_bp
from admin.ui_config import ui_config_bp
from admin.public import public_bp
from admin.tenant import tenant_middleware


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Database
    db_path = os.path.join(app.instance_path, "library.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", f"sqlite:///{db_path}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True

    os.makedirs(app.instance_path, exist_ok=True)

    # Extensions
    db.init_app(app)

    # Multi-tenant middleware
    tenant_middleware(app)

    # Blueprints
    app.register_blueprint(books_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(ui_config_bp)
    app.register_blueprint(public_bp)

    # Health endpoint
    @app.route("/health", methods=["GET"])
    def health():
        from flask import jsonify
        return jsonify({"status": "ok"}), 200

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    from seed import seed_database

    app = create_app()
    seed_database(app)
    app.run(debug=True, port=5000)

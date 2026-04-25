"""Flask application — exposes the AI agent pipeline and authentication as a REST API."""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from auth import auth_bp
from auth.models import User, UserRole, db
from auth.utils import hash_password
from config import Config
from pipeline.orchestrator import Orchestrator

DEFAULT_FORMATS = ["livro", "revista", "hq"]


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)

    _register_pipeline_routes(app)

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _register_pipeline_routes(app):
    @app.route("/health", methods=["GET"])
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    @app.route("/search", methods=["POST"])
    def search() -> tuple:
        """Run the AI pipeline and return the top 3 books.

        Expects JSON body::

            {
                "query": "natural language search",
                "formats": ["book", "comic"]   // optional
            }
        """
        body = request.get_json(silent=True) or {}
        query = body.get("query", "").strip()

        if not query:
            return jsonify({"error": "Query is required"}), 400

        formats: list[str] = body.get("formats") or DEFAULT_FORMATS

        try:
            orchestrator = Orchestrator()
            result = orchestrator.run(query, formats)
            return jsonify(result), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500


def _seed_admin(app):
    """Create a default admin account for the Anhembi Morumbi MVP demo
    if one does not already exist."""
    admin_email = "admin@anhembi.edu.br"
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            email=admin_email,
            password_hash=hash_password("admin123"),
            name="Administrador Anhembi",
            role=UserRole.ADMIN,
            university_slug="anhembi",
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Seed admin created: %s", admin_email)


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from auth import auth_bp
from auth.models import User, UserRole, db
from auth.utils import hash_password
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


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

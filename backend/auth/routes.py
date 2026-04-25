from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from . import auth_bp
from .decorators import admin_required, student_required
from .models import User, UserRole, db
from .utils import hash_password, validate_email, validate_password, verify_password


# ---------------------------------------------------------------------------
# Student endpoints
# ---------------------------------------------------------------------------


@auth_bp.route("/student/register", methods=["POST"])
def student_register():
    """Register a new student account."""
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    university_slug = (data.get("university_slug") or "").strip() or None

    if not email or not name:
        return jsonify({"error": "Email e nome sao obrigatorios."}), 400

    if not validate_email(email):
        return jsonify({"error": "Formato de email invalido."}), 400

    pwd_error = validate_password(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email ja cadastrado."}), 409

    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        role=UserRole.STUDENT,
        university_slug=university_slug,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )

    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/student/login", methods=["POST"])
def student_login():
    """Authenticate a student and return a JWT."""
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email e senha sao obrigatorios."}), 400

    user = User.query.filter_by(email=email, role=UserRole.STUDENT).first()

    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Credenciais invalidas."}), 401

    if not user.is_active:
        return jsonify(
            {"error": "Conta desativada. Entre em contato com o administrador."}
        ), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )

    return jsonify({"token": token, "user": user.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """Authenticate an admin and return a JWT."""
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email e senha sao obrigatorios."}), 400

    user = User.query.filter_by(email=email, role=UserRole.ADMIN).first()

    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Credenciais invalidas."}), 401

    if not user.is_active:
        return jsonify({"error": "Conta desativada."}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )

    return jsonify({"token": token, "user": user.to_dict()}), 200


# ---------------------------------------------------------------------------
# Protected example endpoints (demonstrate RBAC)
# ---------------------------------------------------------------------------


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return the current authenticated user's profile."""
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "Usuario nao encontrado."}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/student/protected", methods=["GET"])
@student_required
def student_protected():
    """Example endpoint accessible only by students."""
    user_id = get_jwt_identity()
    return jsonify(
        {"message": "Acesso de estudante autorizado.", "user_id": user_id}
    ), 200


@auth_bp.route("/admin/protected", methods=["GET"])
@admin_required
def admin_protected():
    """Example endpoint accessible only by admins."""
    user_id = get_jwt_identity()
    return jsonify(
        {"message": "Acesso de administrador autorizado.", "user_id": user_id}
    ), 200

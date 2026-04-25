from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def role_required(*allowed_roles):
    """Decorator that restricts access to users whose JWT role claim
    matches one of *allowed_roles* (``UserRole`` values such as
    ``"student"`` or ``"admin"``).
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in {
                r.value if hasattr(r, "value") else r for r in allowed_roles
            }:
                return jsonify({"error": "Acesso negado. Permissao insuficiente."}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def student_required(fn):
    """Shortcut: only students may access."""
    return role_required("student")(fn)


def admin_required(fn):
    """Shortcut: only admins may access."""
    return role_required("admin")(fn)

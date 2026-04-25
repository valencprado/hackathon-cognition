import re

from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
MIN_PASSWORD_LENGTH = 6


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_password(password: str) -> str | None:
    """Return an error message if the password is invalid, else None."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
    return None

from enum import Enum as PyEnum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserRole(PyEnum):
    STUDENT = "student"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    university_slug = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "university_slug": self.university_slug,
            "is_active": self.is_active,
        }

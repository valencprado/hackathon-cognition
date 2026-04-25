"""Per-tenant UI configuration model."""

import json

from database import db


class UIConfig(db.Model):
    __tablename__ = "ui_configs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant = db.Column(db.String(100), nullable=False, unique=True, index=True)
    university_name = db.Column(db.String(300), nullable=False)
    logo_url = db.Column(db.String(500), nullable=True)
    primary_color = db.Column(db.String(7), nullable=False, default="#1a73e8")
    secondary_color = db.Column(db.String(7), nullable=False, default="#ffffff")
    _custom_labels = db.Column("custom_labels", db.Text, nullable=True)

    @property
    def custom_labels(self):
        if self._custom_labels:
            return json.loads(self._custom_labels)
        return {}

    @custom_labels.setter
    def custom_labels(self, value):
        self._custom_labels = json.dumps(value) if value else None

    def to_dict(self):
        return {
            "id": self.id,
            "tenant": self.tenant,
            "university_name": self.university_name,
            "logo_url": self.logo_url,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "custom_labels": self.custom_labels,
        }

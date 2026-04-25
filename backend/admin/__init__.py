from admin.books import books_bp
from admin.maps import maps_bp
from admin.ui_config import ui_config_bp
from admin.tenant import tenant_middleware

__all__ = ["books_bp", "maps_bp", "ui_config_bp", "tenant_middleware"]

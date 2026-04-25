import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# AI pipeline settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///library.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

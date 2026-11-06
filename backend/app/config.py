# =========================================================
# app/config.py
# Application configuration (Windows-safe paths)
# =========================================================

import os
from pathlib import Path

# Base directory = backend folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Convert Windows backslashes to forward slashes for SQLite URI
_db_path = (BASE_DIR / "data" / "inventory.db").as_posix()


class Config:
    """Base configuration."""

    # ---------- Flask ----------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # ---------- Database ----------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{_db_path}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- File uploads ----------
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload

    # ---------- Recognition ----------
    MODEL_PATH = str(BASE_DIR / 'models' / 'recognizer.pth')
    CLASS_MAP_PATH = str(BASE_DIR / 'data' / 'item_classes.json')

    CONFIDENCE_SUCCESS = 0.75
    CONFIDENCE_LOW = 0.40

    # ---------- CORS ----------
    CORS_ORIGINS = [
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'http://localhost:3000',
    ]

    # ---------- Email (For Password Reset) ----------
    MAIL_EMAIL = os.environ.get('MAIL_EMAIL')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5500')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')   # must be set in prod
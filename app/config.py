"""
Application configuration.

Values are read from environment variables (populated from .env via
python-dotenv in app/__init__.py). Keep this file free of any real
secrets — .env is gitignored and holds the actual values.
"""

import os


class Config:
    """Base config shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///cdoe.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email / IMAP (used starting Phase 6)
    IMAP_HOST = os.environ.get("IMAP_HOST")
    IMAP_PORT = int(os.environ.get("IMAP_PORT", 993))
    IMAP_USER = os.environ.get("IMAP_USER")
    IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD")
    IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX")
    IMAP_USE_SSL = os.environ.get("IMAP_USE_SSL", "true").lower() == "true"

    # Scheduler (used starting Phase 6)
    SYNC_INTERVAL_MINUTES = int(os.environ.get("SYNC_INTERVAL_MINUTES", 2))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

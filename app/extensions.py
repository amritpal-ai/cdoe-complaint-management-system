"""
Shared extension instances.

Created here (unbound) and initialized against the app inside the
application factory in app/__init__.py. This avoids circular imports:
models.py and services.py can `from app.extensions import db` without
ever importing the factory itself.

APScheduler is intentionally NOT included yet -- it has nothing to
schedule until email_service functionality exists in Phase 6. Adding it
now would be an unused abstraction; it will be added back here when it's
actually needed.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
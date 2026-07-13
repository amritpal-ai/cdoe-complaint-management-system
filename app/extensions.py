"""
Shared extension instances.

Created here (unbound) and initialized against the app inside the
application factory in app/__init__.py. This avoids circular imports:
models and services can `from app.extensions import db` without ever
importing the factory itself.
"""

from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
scheduler = BackgroundScheduler()

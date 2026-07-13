from flask import Blueprint

email_sync_bp = Blueprint("email_sync", __name__, url_prefix="/email-sync")

from app.blueprints.email_sync import routes  # noqa: E402,F401

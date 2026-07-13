from flask import Blueprint

# This is the ONLY user-facing page in the application (per v2 architecture:
# no separate ticket details page — everything expands inline on this screen).
dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder="../../templates/dashboard",
)

from app.blueprints.dashboard import routes  # noqa: E402,F401

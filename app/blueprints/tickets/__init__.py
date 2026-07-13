from flask import Blueprint

# All ticket actions (manual create, title edit, add remark, close, reopen,
# mark duplicate) live here as AJAX endpoints only. This blueprint never
# renders a full page — it returns HTML partials or JSON that dashboard.js
# swaps into the already-expanded ticket row.
tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")

from app.blueprints.tickets import routes  # noqa: E402,F401

"""
Routes for the CDOE Complaint Management System.

Everything lives in one blueprint in one file — this is a small, single-PC
internal tool with one working screen (the dashboard, per architecture),
so splitting routes across multiple blueprint packages would be
unnecessary structure for the amount of code involved.

Phase 1 scope is data layer only: no ticket CRUD, no dashboard data, no
timeline/remarks logic yet. The route below is unchanged from Phase 0 —
it still renders the static placeholder page.
"""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    The single working screen of the application.

    Still a placeholder in Phase 1 — real ticket data, status cards, and
    inline row expansion arrive starting Phase 2, once services.py has
    ticket_service-style functions to query/create tickets.
    """
    return render_template("dashboard/index.html")
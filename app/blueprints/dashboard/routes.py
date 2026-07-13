from flask import render_template

from app.blueprints.dashboard import dashboard_bp


@dashboard_bp.route("/")
def index():
    """
    The single working screen of the application.

    Phase 0: renders a static placeholder so we can confirm the app boots
    end-to-end (factory -> blueprint -> template -> Bootstrap).

    Starting Phase 2, this will query real tickets via ticket_service and
    render the status cards + ticket table, with each row expanding inline
    for all ticket actions (no separate ticket detail page).
    """
    return render_template("dashboard/index.html")

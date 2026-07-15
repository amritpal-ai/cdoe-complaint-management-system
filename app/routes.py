"""
Routes for the CDOE Complaint Management System.

Everything lives in one blueprint in one file — this is a small, single-PC
internal tool with one working screen (the dashboard, per architecture),
so splitting routes across multiple blueprint packages would be
unnecessary structure for the amount of code involved.

Phase 4.5 scope: dashboard UI/UX cleanup on top of Phase 4's remarks/
timeline system — no new business logic. Close/reopen/mark-duplicate and
the email-sync endpoint are added to this same file in later phases.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import services
from app.models import Ticket, Remark

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    The single working screen of the application.

    Lists all existing tickets, newest first, plus live counts per status
    for the summary cards. Each ticket also gets a transient
    `latest_remark` attribute (not a DB column — computed here per
    request) for the dashboard's "Latest Remark" column.

    `expanded` is an optional query-string ticket id — when present, that
    ticket's row renders already expanded. It's kept for deep-linking to
    a specific ticket's full history, but is no longer set automatically
    after adding a remark (that UI moved to a row-level modal in Phase
    4.5, so adding a remark no longer requires expanding the row).
    """
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()

    for ticket in tickets:
        ticket.latest_remark = (
            ticket.remarks.order_by(Remark.created_at.desc()).first()
        )

    counts = {
        "New": Ticket.query.filter_by(status="New").count(),
        "In Progress": Ticket.query.filter_by(status="In Progress").count(),
        "Closed": Ticket.query.filter_by(status="Closed").count(),
        "Reopened": Ticket.query.filter_by(status="Reopened").count(),
    }

    expanded_ticket_id = request.args.get("expanded", type=int)

    return render_template(
        "dashboard/index.html",
        tickets=tickets,
        counts=counts,
        expanded_ticket_id=expanded_ticket_id,
    )


@main_bp.route("/tickets", methods=["POST"])
def create_ticket():
    """
    Handle the "+ New Complaint" modal submission.

    Source is always 'Manual' here — this endpoint is the only way a
    Manual ticket gets created. Status is always 'New' (enforced inside
    services.create_ticket, never taken from the form).
    """
    title = request.form.get("title", "").strip()
    original_complaint = request.form.get("original_complaint", "").strip()

    if not title or not original_complaint:
        flash("Title and Original Complaint are both required.", "danger")
        return redirect(url_for("main.index"))

    services.create_ticket(
        title=title,
        original_complaint=original_complaint,
        source="Manual",
    )
    flash("Ticket created successfully.", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/tickets/<int:ticket_id>/remarks", methods=["POST"])
def add_remark(ticket_id):
    """
    Handle a remark submission from a row-level "Add Remark" modal.

    Redirects back to the plain dashboard (no forced expand) — the
    dashboard stays compact, and the new remark is immediately visible
    via the "Latest Remark" column and updated status badge/counts. The
    full timeline and remark history are still available by expanding
    the row, but that's optional now, not required to see this update.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    body = request.form.get("body", "").strip()

    if not body:
        flash("Remark cannot be empty.", "danger")
        return redirect(url_for("main.index"))

    try:
        services.add_remark(ticket, body)
        flash("Remark added.", "success")
    except services.TicketClosedError as e:
        flash(str(e), "danger")

    return redirect(url_for("main.index"))
"""
Routes for the CDOE Complaint Management System.

Everything lives in one blueprint in one file — this is a small, single-PC
internal tool with one working screen (the dashboard, per architecture),
so splitting routes across multiple blueprint packages would be
unnecessary structure for the amount of code involved.

Phase 2 scope: manual ticket creation, and listing existing tickets on the
dashboard. Ticket-action endpoints (remarks, close, reopen, mark
duplicate) and the email-sync endpoint are added to this same file in
later phases.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import services
from app.models import Ticket

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    The single working screen of the application.

    Lists all existing tickets, newest first. Row expansion, remarks,
    timeline display, and status actions (close/reopen/duplicate) are not
    wired up yet — the expand button is present but inert until Phase 3.
    """
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("dashboard/index.html", tickets=tickets)


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
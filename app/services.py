"""
Service layer — business logic lives here, kept separate from routes.py
so route handlers stay thin (parse request -> call service -> respond).

Phase 4 scope: manual ticket creation, and the remarks/timeline system.

Functions added later: close_ticket(), reopen_ticket(), mark_duplicate(),
and (Phase 6) sync_emails().
"""

from app.extensions import db
from app.models import Ticket, TimelineEvent, Remark


class TicketClosedError(Exception):
    """Raised when a remark is attempted on a Closed ticket."""


def log_event(ticket_id, event, details=None):
    """
    Write a single TimelineEvent row.

    This is the ONLY place in the app that should construct a
    TimelineEvent — every ticket-mutating function calls this so the
    audit log can never drift from the actual state changes it describes.

    Does NOT commit. The caller adds this to the same transaction as the
    state change it's logging, and commits once at the end.
    """
    entry = TimelineEvent(ticket_id=ticket_id, event=event, details=details)
    db.session.add(entry)
    return entry


def create_ticket(title, original_complaint, source="Manual"):
    """
    Create a new ticket.

    Status always starts at 'New' — this is never set manually by a
    caller, per the ticket workflow rules. Writes a single 'Ticket
    Created' timeline entry in the same transaction as the insert, so the
    ticket and its first timeline entry are always created together.
    """
    ticket = Ticket(
        title=title.strip(),
        original_complaint=original_complaint.strip(),
        source=source,
        status="New",
    )
    db.session.add(ticket)
    db.session.flush()  # assigns ticket.id without ending the transaction

    log_event(ticket.id, event="Ticket Created", details="Ticket created")

    db.session.commit()
    return ticket


def add_remark(ticket, body):
    """
    Add a remark to a ticket.

    Rules (per ticket workflow):
      - Closed tickets reject new remarks entirely — the caller must
        reopen the ticket first. Raises TicketClosedError; no Remark or
        TimelineEvent is written in that case.
      - If this is the ticket's first remark (status == 'New'), status
        automatically flips to 'In Progress' and a second 'Status
        Changed' timeline entry is written recording the transition.
      - If the ticket is already 'In Progress' (or 'Reopened' — handled
        the same way once reopen exists), the remark is saved and a
        timeline entry is written, but status is left unchanged.

    Takes a Ticket instance (not an id) since the caller (route handler)
    already looked it up via get_or_404 — avoids a second query.
    """
    if ticket.status == "Closed":
        raise TicketClosedError(
            "This ticket is closed. Reopen it before adding remarks."
        )

    body = body.strip()

    remark = Remark(ticket_id=ticket.id, body=body)
    db.session.add(remark)

    log_event(ticket.id, event="Remark Added", details=body)

    if ticket.status == "New":
        old_status = ticket.status
        ticket.status = "In Progress"
        log_event(
            ticket.id,
            event="Status Changed",
            details=f"{old_status} → In Progress",
        )
    # Already 'In Progress' (or any other non-Closed status): no status change.

    db.session.commit()
    return remark
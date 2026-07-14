"""
Service layer — business logic lives here, kept separate from routes.py
so route handlers stay thin (parse request -> call service -> respond).

Phase 2 scope: manual ticket creation only.

Functions added later (Phase 3+): add_remark(), close_ticket(),
reopen_ticket(), mark_duplicate(), and (Phase 6) sync_emails().
"""

from app.extensions import db
from app.models import Ticket, TimelineEvent


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
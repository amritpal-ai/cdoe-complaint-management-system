"""
Service layer — business logic lives here, kept separate from routes.py
so route handlers stay thin (parse request -> call service -> respond).

Phase 5 scope: manual ticket creation, the remarks/timeline system, and
the full ticket lifecycle (close, reopen, mark as duplicate).

Function added later: sync_emails() (Phase 6).
"""

from app.extensions import db
from app.models import Ticket, TimelineEvent, Remark


class TicketClosedError(Exception):
    """Raised when a remark is attempted on a Closed ticket."""


class InvalidTransitionError(Exception):
    """Raised when a lifecycle action is attempted from an invalid status."""


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
      - If this is the ticket's first remark (status == 'New'), or the
        first remark after being reopened (status == 'Reopened'), status
        automatically flips to 'In Progress' and a second 'Status
        Changed' timeline entry is written recording the transition.
      - If the ticket is already 'In Progress', the remark is saved and
        a timeline entry is written, but status is left unchanged.

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

    if ticket.status in ("New", "Reopened"):
        old_status = ticket.status
        ticket.status = "In Progress"
        log_event(
            ticket.id,
            event="Status Changed",
            details=f"{old_status} → In Progress",
        )
    # Already 'In Progress': no status change.

    db.session.commit()
    return remark


def close_ticket(ticket):
    """
    Close a ticket.

    Valid from any non-Closed status. Writes a single 'Ticket Closed'
    timeline entry. The route layer is responsible for the "are you
    sure?" confirmation — this function just performs the transition.
    """
    if ticket.status == "Closed":
        raise InvalidTransitionError("This ticket is already closed.")

    ticket.status = "Closed"
    log_event(ticket.id, event="Ticket Closed")

    db.session.commit()
    return ticket


def reopen_ticket(ticket):
    """
    Reopen a ticket.

    Only valid from 'Closed' — this is the only way a ticket becomes
    'Reopened'. Writes a single 'Ticket Reopened' timeline entry. Status
    stays 'Reopened' until the next remark, which flips it to
    'In Progress' (see add_remark above).
    """
    if ticket.status != "Closed":
        raise InvalidTransitionError("Only closed tickets can be reopened.")

    ticket.status = "Reopened"
    log_event(ticket.id, event="Ticket Reopened")

    db.session.commit()
    return ticket


def mark_duplicate(ticket, original_ticket):
    """
    Mark `ticket` as a duplicate of `original_ticket`.

    Rules:
      - A ticket cannot be marked as a duplicate of itself.
      - The original ticket must currently be open (New, In Progress, or
        Reopened) — marking something a duplicate of an already-closed
        ticket wouldn't make sense for staff following up on it.
      - `ticket.duplicate_of_ticket_id` is set, `ticket.status` becomes
        'Closed'.
      - A timeline entry is written on `ticket` recording what it was
        linked to, and a separate timeline entry is written on
        `original_ticket` recording that a duplicate was linked to it —
        so anyone reviewing either ticket sees the connection.
    """
    if ticket.id == original_ticket.id:
        raise InvalidTransitionError(
            "A ticket cannot be marked as a duplicate of itself."
        )
    if original_ticket.status not in ("New", "In Progress", "Reopened"):
        raise InvalidTransitionError(
            "You can only mark a ticket as a duplicate of an open ticket."
        )

    ticket.duplicate_of_ticket_id = original_ticket.id
    ticket.status = "Closed"

    log_event(
        ticket.id,
        event=f"Marked as Duplicate of Ticket #{original_ticket.id}",
    )
    log_event(
        original_ticket.id,
        event="Duplicate Complaint Linked",
        details=f"Ticket #{ticket.id}",
    )

    db.session.commit()
    return ticket
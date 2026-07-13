"""
Database models for the CDOE Complaint Management System.

Three tables only, kept deliberately minimal per project scope:
  - Ticket          the complaint itself
  - Remark          internal notes staff add to a ticket
  - TimelineEvent   permanent, append-only audit log per ticket

This is a single-PC SQLite app with no auth and no scaling requirements,
so all models live together in one file rather than a models/ package —
splitting three small classes into separate files would add navigation
overhead without improving readability.

Relationships:
  Ticket 1---N Remark
  Ticket 1---N TimelineEvent
  Ticket 1---1 Ticket   (optional self-reference for duplicate marking)
"""

from datetime import datetime

from app.extensions import db


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    # Email subject (for email tickets) or staff-entered text (for manual
    # tickets). Editable afterwards from the dashboard.
    title = db.Column(db.String(255), nullable=False)

    # Full complaint text: email body, or manually typed complaint.
    original_complaint = db.Column(db.Text, nullable=False)

    # 'Email' or 'Manual'
    source = db.Column(db.String(20), nullable=False)

    # 'New' | 'In Progress' | 'Closed' | 'Reopened'
    status = db.Column(db.String(20), nullable=False, default="New")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Set when this ticket is marked as a duplicate of another ticket.
    # Nullable self-reference — most tickets will have this as NULL.
    duplicate_of_ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), nullable=True
    )
    duplicate_of = db.relationship(
        "Ticket", remote_side=[id], backref="duplicates"
    )

    # Only populated for source='Email'. This is the sole mechanism used to
    # prevent importing the same email twice — enforced with a UNIQUE index
    # at the database level, not just an application-level check.
    message_id = db.Column(db.String(998), unique=True, nullable=True)

    # Related remarks / timeline events. cascade delete keeps things tidy if
    # a ticket is ever removed (not exposed in the UI, but useful in tests).
    remarks = db.relationship(
        "Remark",
        backref="ticket",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    timeline_events = db.relationship(
        "TimelineEvent",
        backref="ticket",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint("source IN ('Email', 'Manual')", name="ck_ticket_source"),
        db.CheckConstraint(
            "status IN ('New', 'In Progress', 'Closed', 'Reopened')",
            name="ck_ticket_status",
        ),
        db.Index("ix_tickets_status", "status"),
        db.Index("ix_tickets_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Ticket #{self.id} [{self.status}] {self.title!r}>"


class Remark(db.Model):
    __tablename__ = "remarks"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), nullable=False, index=True
    )
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Remark #{self.id} on Ticket #{self.ticket_id}>"


class TimelineEvent(db.Model):
    __tablename__ = "timeline_events"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("tickets.id"), nullable=False, index=True
    )

    # Short machine-readable event name, e.g. 'TICKET_CREATED', 'STATUS_CHANGED'
    event = db.Column(db.String(50), nullable=False)

    # Human-readable detail, e.g. "Status changed from New to In Progress"
    details = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<TimelineEvent #{self.id} {self.event} (Ticket #{self.ticket_id})>"
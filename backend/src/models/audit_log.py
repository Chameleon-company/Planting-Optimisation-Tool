"""
Audit Log Model

SQLAlchemy model for tracking security-relevant events and user actions.
Provides an immutable audit trail for compliance, security monitoring, and forensics.
"""

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.database import Base
from datetime import datetime, timezone


class AuditLog(Base):
    """
    Audit log database model for security and compliance tracking.

    Records important user actions and system events for accountability,
    security monitoring, and regulatory compliance. Audit logs should be
    treated as append-only and never modified or deleted.

    Attributes:
        id: Primary key, unique identifier for the log entry
        user_id: Foreign key to users table - who performed the action
        event_type: Category of event (indexed for fast filtering)
        details: Detailed description of what happened
        timestamp: When the event occurred (UTC, auto-set on creation)
        user: Relationship to User model - the user who triggered the event

    Common Event Types:
        - "user_create": New user account created
        - "user_update": User account modified
        - "user_delete": User account deleted
        - "login": Successful authentication
        - "login_failed": Failed authentication attempt
        - "role_change": User role modified
        - "password_change": User password changed

    Usage Example:
        from src.services.authentication import log_audit_event

        await log_audit_event(
            db=db,
            user_id=current_user.id,
            event_type="user_create",
            details=f"Created user {new_user.email} with role {new_user.role}"
        )

    Security & Compliance:
        - Provides accountability for user actions
        - Helps detect suspicious activity patterns
        - Required for many security standards (SOC 2, ISO 27001, etc.)
        - Useful for incident response and forensics
        - Should be backed up and protected from tampering

    Database Schema:
        - Table name: audit_logs
        - Indexes on: id, event_type (for fast queries)
        - Foreign key: user_id -> users.id
        - Auto-timestamp on insert

    Best Practices:
        - Never modify or delete audit logs (append-only)
        - Include enough detail to understand what happened
        - Log both successful and failed security-relevant actions
        - Protect audit logs with appropriate access controls
        - Regularly review logs for anomalies
    """

    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Who performed the action
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # What type of event occurred (indexed for fast filtering)
    event_type: Mapped[str] = mapped_column(index=True)

    # Detailed description of the event
    details: Mapped[str] = mapped_column()

    # When the event occurred (UTC, auto-set on creation)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to User model
    user = relationship("User")

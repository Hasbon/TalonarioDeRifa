from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit(
    db: Session,
    *,
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    previous_values: dict | None = None,
    new_values: dict | None = None,
    reason: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_values=previous_values,
        new_values=new_values,
        reason=reason,
    )
    db.add(entry)
    return entry

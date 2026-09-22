from datetime import datetime

from fastapi import HTTPException, status

from app.repositories.store import Store
from app.schemas.common import SessionStatus
from app.schemas.models import Session
from app.services import schedule_service


def _reject(message: str) -> None:
    raise HTTPException(status.HTTP_409_CONFLICT, detail=message)


def find(store: Store, session_id: str) -> Session:
    for session in store.sessions:
        if session.id == session_id:
            return session
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, detail="That booking no longer exists."
    )


def list_sessions(store: Store, status_filter: SessionStatus | None) -> list[Session]:
    sessions = store.sessions
    if status_filter is not None:
        sessions = [s for s in sessions if s.status == status_filter]
    return sorted(sessions, key=lambda s: s.starts_at)


def accept(store: Store, session_id: str) -> Session:
    session = find(store, session_id)
    if session.status != SessionStatus.pending:
        _reject("This request has already been handled.")
    schedule_service.guard_slot_free(store, session.starts_at, session.id)
    session.status = SessionStatus.upcoming
    return session


def decline(store: Store, session_id: str) -> Session:
    session = find(store, session_id)
    if session.status != SessionStatus.pending:
        _reject("This request has already been handled.")
    session.status = SessionStatus.declined
    return session


def complete(store: Store, session_id: str, remarks: str | None) -> Session:
    session = find(store, session_id)
    if session.status != SessionStatus.upcoming:
        _reject("Only upcoming sessions can be completed.")
    trimmed = (remarks or "").strip()
    session.status = SessionStatus.completed
    session.remarks = trimmed or None
    return session


def reschedule(store: Store, session_id: str, starts_at: datetime) -> Session:
    session = find(store, session_id)
    if session.status != SessionStatus.upcoming:
        _reject("Only upcoming sessions can be moved.")
    if session.starts_at == starts_at:
        _reject("That is the same time this session already has.")
    schedule_service.guard_slot_free(store, starts_at, session.id)
    session.starts_at = starts_at
    return session

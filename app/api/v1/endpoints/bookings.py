from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import Store, get_store
from app.schemas.common import SessionStatus
from app.schemas.models import Session
from app.schemas.requests import CompleteSession, RescheduleSession
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _parse(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="startsAt must be an ISO 8601 date and time.",
        )


@router.get("", response_model=list[Session], response_model_by_alias=True)
def list_bookings(
    status_filter: SessionStatus | None = Query(default=None, alias="status"),
    store: Store = Depends(get_store),
) -> list[Session]:
    return booking_service.list_sessions(store, status_filter)


@router.get("/{session_id}", response_model=Session, response_model_by_alias=True)
def read_booking(session_id: str, store: Store = Depends(get_store)) -> Session:
    return booking_service.find(store, session_id)


@router.post("/{session_id}/accept", response_model=Session, response_model_by_alias=True)
def accept_booking(session_id: str, store: Store = Depends(get_store)) -> Session:
    return booking_service.accept(store, session_id)


@router.post("/{session_id}/decline", response_model=Session, response_model_by_alias=True)
def decline_booking(session_id: str, store: Store = Depends(get_store)) -> Session:
    return booking_service.decline(store, session_id)


@router.post("/{session_id}/complete", response_model=Session, response_model_by_alias=True)
def complete_booking(
    session_id: str,
    payload: CompleteSession | None = None,
    store: Store = Depends(get_store),
) -> Session:
    remarks = payload.remarks if payload is not None else None
    return booking_service.complete(store, session_id, remarks)


@router.post(
    "/{session_id}/reschedule", response_model=Session, response_model_by_alias=True
)
def reschedule_booking(
    session_id: str,
    payload: RescheduleSession,
    store: Store = Depends(get_store),
) -> Session:
    return booking_service.reschedule(store, session_id, _parse(payload.starts_at))

from datetime import datetime

from fastapi import HTTPException, status

from app.repositories.store import Store
from app.schemas.common import SessionStatus
from app.schemas.models import Note, Patient, PatientDetail, Session


def _completed_for(store: Store, patient_id: str) -> list[Session]:
    return sorted(
        (
            s
            for s in store.sessions
            if s.patient_id == patient_id and s.status == SessionStatus.completed
        ),
        key=lambda s: s.starts_at,
        reverse=True,
    )


def list_patients(store: Store) -> list[PatientDetail]:
    return [_detail(store, patient) for patient in store.patients]


def get_patient(store: Store, patient_id: str) -> PatientDetail:
    for patient in store.patients:
        if patient.id == patient_id:
            return _detail(store, patient)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="That patient was not found.")


# Last session and history are derived, so completing a session moves them at once.
def _detail(store: Store, patient: Patient) -> PatientDetail:
    history = _completed_for(store, patient.id)
    return PatientDetail(
        **patient.model_dump(),
        last_session_at=history[0].starts_at if history else None,
        previous_sessions=history,
    )


def list_notes(store: Store, patient_id: str | None) -> list[Note]:
    notes = store.notes
    if patient_id is not None:
        notes = [n for n in notes if n.patient_id == patient_id]
    return sorted(notes, key=lambda n: n.created_at, reverse=True)


def _clean(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]


def _optional(value: str | None) -> str | None:
    trimmed = (value or "").strip()
    return trimmed or None


def add_note(
    store: Store,
    patient_id: str,
    note: str,
    exercises: list[str],
    next_session_plan: str | None,
) -> Note:
    get_patient(store, patient_id)
    created = Note(
        id=f"note-{int(datetime.now().timestamp() * 1_000_000)}",
        patient_id=patient_id,
        note=note.strip(),
        exercises=_clean(exercises),
        next_session_plan=_optional(next_session_plan),
        created_at=datetime.now(),
    )
    store.notes.append(created)
    return created


def edit_note(
    store: Store,
    note_id: str,
    note: str,
    exercises: list[str],
    next_session_plan: str | None,
) -> Note:
    for existing in store.notes:
        if existing.id == note_id:
            existing.note = note.strip()
            existing.exercises = _clean(exercises)
            existing.next_session_plan = _optional(next_session_plan)
            existing.updated_at = datetime.now()
            return existing
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="That note no longer exists.")

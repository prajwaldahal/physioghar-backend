from fastapi import APIRouter, Depends, Query, status

from app.api.deps import Store, get_store
from app.schemas.models import Note, PatientDetail
from app.schemas.requests import NoteCreate, NoteUpdate
from app.services import patient_service

router = APIRouter(tags=["patients"])


@router.get(
    "/patients", response_model=list[PatientDetail], response_model_by_alias=True
)
def list_patients(store: Store = Depends(get_store)) -> list[PatientDetail]:
    return patient_service.list_patients(store)


@router.get(
    "/patients/{patient_id}",
    response_model=PatientDetail,
    response_model_by_alias=True,
)
def read_patient(patient_id: str, store: Store = Depends(get_store)) -> PatientDetail:
    return patient_service.get_patient(store, patient_id)


@router.get("/notes", response_model=list[Note], response_model_by_alias=True)
def list_notes(
    patient_id: str | None = Query(default=None, alias="patientId"),
    store: Store = Depends(get_store),
) -> list[Note]:
    return patient_service.list_notes(store, patient_id)


@router.post(
    "/notes",
    response_model=Note,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_note(payload: NoteCreate, store: Store = Depends(get_store)) -> Note:
    return patient_service.add_note(
        store,
        payload.patient_id,
        payload.note,
        payload.exercises,
        payload.next_session_plan,
    )


@router.put("/notes/{note_id}", response_model=Note, response_model_by_alias=True)
def update_note(
    note_id: str, payload: NoteUpdate, store: Store = Depends(get_store)
) -> Note:
    return patient_service.edit_note(
        store,
        note_id,
        payload.note,
        payload.exercises,
        payload.next_session_plan,
    )

from fastapi import APIRouter, Depends, status

from app.api.deps import Store, get_store
from app.schemas.models import Complaint
from app.schemas.requests import ComplaintCreate
from app.services import complaint_service

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.get("", response_model=list[Complaint], response_model_by_alias=True)
def list_complaints(store: Store = Depends(get_store)) -> list[Complaint]:
    return complaint_service.list_complaints(store)


@router.post(
    "",
    response_model=Complaint,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_complaint(
    payload: ComplaintCreate, store: Store = Depends(get_store)
) -> Complaint:
    return complaint_service.create_complaint(
        store, payload.category, payload.subject, payload.description
    )

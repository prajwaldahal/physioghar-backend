from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import Store, get_store
from app.schemas.models import ResolvedSlot
from app.schemas.requests import SlotCreate
from app.services import schedule_service

router = APIRouter(prefix="/slots", tags=["slots"])


def _parse(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="startsAt must be an ISO 8601 date and time.",
        )


@router.get("", response_model=list[ResolvedSlot], response_model_by_alias=True)
def list_slots(
    day: date | None = Query(
        default=None, description="Day to list slots for; omit for the whole horizon"
    ),
    store: Store = Depends(get_store),
) -> list[ResolvedSlot]:
    scoped = datetime(day.year, day.month, day.day) if day is not None else None
    return schedule_service.resolve_day(store, scoped)


@router.post(
    "",
    response_model=ResolvedSlot,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_slot(
    payload: SlotCreate, store: Store = Depends(get_store)
) -> ResolvedSlot:
    return schedule_service.add_slot(store, _parse(payload.starts_at))


@router.post(
    "/{slot_id}/block", response_model=ResolvedSlot, response_model_by_alias=True
)
def block_slot(slot_id: str, store: Store = Depends(get_store)) -> ResolvedSlot:
    return schedule_service.block(store, slot_id)


@router.post(
    "/{slot_id}/unblock", response_model=ResolvedSlot, response_model_by_alias=True
)
def unblock_slot(slot_id: str, store: Store = Depends(get_store)) -> ResolvedSlot:
    return schedule_service.unblock(store, slot_id)

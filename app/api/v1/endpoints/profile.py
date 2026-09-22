from fastapi import APIRouter, Depends

from app.api.deps import Store, get_store
from app.schemas.models import AvailabilityStatus, Profile
from app.schemas.requests import AvailabilityUpdate, ProfileUpdate
from app.services import profile_service

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=Profile, response_model_by_alias=True)
def read_profile(store: Store = Depends(get_store)) -> Profile:
    return profile_service.get_profile(store)


@router.put("/profile", response_model=Profile, response_model_by_alias=True)
def write_profile(
    payload: ProfileUpdate, store: Store = Depends(get_store)
) -> Profile:
    return profile_service.update_profile(store, payload.model_dump())


@router.get("/availability", response_model=AvailabilityStatus)
def read_availability(store: Store = Depends(get_store)) -> AvailabilityStatus:
    return AvailabilityStatus(available=profile_service.get_availability(store))


@router.put("/availability", response_model=AvailabilityStatus)
def write_availability(
    payload: AvailabilityUpdate, store: Store = Depends(get_store)
) -> AvailabilityStatus:
    return AvailabilityStatus(
        available=profile_service.set_availability(store, payload.available)
    )

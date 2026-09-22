from fastapi import APIRouter

from app.api.v1.endpoints import bookings, patients, profile, slots

api_router = APIRouter()
api_router.include_router(profile.router)
api_router.include_router(slots.router)
api_router.include_router(bookings.router)
api_router.include_router(patients.router)

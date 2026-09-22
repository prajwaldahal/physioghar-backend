from fastapi import APIRouter

from app.api.v1.endpoints import profile, slots

api_router = APIRouter()
api_router.include_router(profile.router)
api_router.include_router(slots.router)

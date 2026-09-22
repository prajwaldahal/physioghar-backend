from app.repositories.store import Store
from app.schemas.models import Profile


def get_profile(store: Store) -> Profile:
    return store.profile


def update_profile(store: Store, changes: dict) -> Profile:
    store.profile = store.profile.model_copy(update=changes)
    return store.profile


def get_availability(store: Store) -> bool:
    return store.available


def set_availability(store: Store, available: bool) -> bool:
    store.available = available
    return store.available

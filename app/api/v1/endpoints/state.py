from fastapi import APIRouter, Depends

from app.api.deps import Store, get_store

router = APIRouter(tags=["state"])


# Backs the app's logout, which puts the demo data back to its seed.
@router.post("/reset")
def reset_state(store: Store = Depends(get_store)) -> dict[str, str]:
    store.reset()
    return {"status": "reset"}

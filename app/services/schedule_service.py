from datetime import datetime

from fastapi import HTTPException, status

from app.repositories.store import Store
from app.schemas.common import HOLDS_SLOT, SlotAvailability, SlotState
from app.schemas.models import ResolvedSlot, Slot
from app.utils.dates import overlaps, start_of_week


def _reject(message: str) -> None:
    raise HTTPException(status.HTTP_409_CONFLICT, detail=message)


def _holders(store: Store) -> dict[datetime, object]:
    return {s.starts_at: s for s in store.sessions if s.status in HOLDS_SLOT}


def resolve_day(store: Store, day: datetime) -> list[ResolvedSlot]:
    holders = _holders(store)
    resolved = []
    for slot in store.slots:
        if slot.starts_at.date() != day.date():
            continue
        session = holders.get(slot.starts_at)
        if session is not None:
            state = SlotState.booked
        elif slot.availability == SlotAvailability.blocked:
            state = SlotState.blocked
        else:
            state = SlotState.open
        resolved.append(
            ResolvedSlot(
                id=slot.id,
                starts_at=slot.starts_at,
                state=state,
                session=session,
            )
        )
    return sorted(resolved, key=lambda s: s.starts_at)


def find_slot(store: Store, slot_id: str) -> Slot:
    for slot in store.slots:
        if slot.id == slot_id:
            return slot
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="That slot no longer exists.")


def block(store: Store, slot_id: str) -> ResolvedSlot:
    slot = find_slot(store, slot_id)
    if slot.availability == SlotAvailability.blocked:
        _reject("That slot is already blocked.")
    if slot.starts_at in _holders(store):
        _reject("A booked slot cannot be blocked. Move or complete the session first.")
    slot.availability = SlotAvailability.blocked
    return _single(store, slot)


def unblock(store: Store, slot_id: str) -> ResolvedSlot:
    slot = find_slot(store, slot_id)
    if slot.availability != SlotAvailability.blocked:
        _reject("That slot is already open.")
    slot.availability = SlotAvailability.open
    return _single(store, slot)


def add_slot(store: Store, starts_at: datetime) -> ResolvedSlot:
    for slot in store.slots:
        if overlaps(slot.starts_at, starts_at):
            _reject("That overlaps a slot you already have on this day.")
    created = Slot(
        id=f"added-{int(starts_at.timestamp())}",
        starts_at=starts_at,
        availability=SlotAvailability.open,
    )
    store.slots.append(created)
    store.slots.sort(key=lambda s: s.starts_at)
    return _single(store, created)


# Accepting and rescheduling both need the same guarantee: a slot exists at that
# time, it is not blocked, and nobody else already holds it.
def guard_slot_free(store: Store, starts_at: datetime, ignore_session_id: str) -> None:
    for session in store.sessions:
        if (
            session.id != ignore_session_id
            and session.status in HOLDS_SLOT
            and session.starts_at == starts_at
        ):
            _reject("That time is already booked. Pick another slot.")

    match = [s for s in store.slots if s.starts_at == starts_at]
    if not match:
        _reject("There is no slot at that time. Add one from the schedule first.")
    if match[0].availability == SlotAvailability.blocked:
        _reject("That slot is blocked. Unblock it or pick another time.")


def _single(store: Store, slot: Slot) -> ResolvedSlot:
    for resolved in resolve_day(store, slot.starts_at):
        if resolved.id == slot.id:
            return resolved
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="That slot no longer exists.")

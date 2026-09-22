import json
from datetime import datetime, timedelta
from pathlib import Path

from app.schemas.common import SlotAvailability
from app.schemas.models import Complaint, Note, Patient, Profile, Session, Slot
from app.utils.dates import resolve_date, start_of_week

SEED_DIR = Path(__file__).parent / "seed"


def _read(name: str):
    return json.loads((SEED_DIR / f"{name}.json").read_text())


def _session(row: dict) -> Session:
    return Session(
        id=row["id"],
        patient_id=row["patientId"],
        patient_name=row["patientName"],
        treatment=row["treatment"],
        location=row["location"],
        starts_at=resolve_date(row["dayOffset"], row["time"]),
        status=row["status"],
        remarks=row.get("remarks"),
    )


def _patient(row: dict) -> Patient:
    return Patient(
        id=row["id"],
        name=row["name"],
        age=row["age"],
        gender=row["gender"],
        phone=row["phone"],
        condition=row["condition"],
        treatment_history=row["treatmentHistory"],
    )


def _note(row: dict) -> Note:
    return Note(
        id=row["id"],
        patient_id=row["patientId"],
        note=row["note"],
        exercises=row["exercises"],
        next_session_plan=row.get("nextSessionPlan"),
        created_at=resolve_date(row["dayOffset"], row["time"]),
    )


def _complaint(row: dict) -> Complaint:
    return Complaint(
        id=row["id"],
        reference=row["reference"],
        category=row["category"],
        subject=row["subject"],
        description=row["description"],
        status=row["status"],
        created_at=resolve_date(row["dayOffset"], row["time"]),
    )


def _profile(row: dict) -> Profile:
    return Profile(
        name=row["name"],
        email=row["email"],
        phone=row["phone"],
        experience_years=row["experienceYears"],
        specialization=row["specialization"],
        address=row["address"],
    )


# Built from a per-weekday template rather than fixed dates so the seeded week
# looks the same whichever day the API is started.
def _slots() -> list[Slot]:
    config = _read("slots")
    hours = config["hours"]
    weekdays = config["weekdays"]
    monday = start_of_week(datetime.now().date())

    slots: list[Slot] = []
    for day in range(config["horizonDays"]):
        current = monday + timedelta(days=day)
        template = weekdays[str(current.isoweekday())]
        for hour in hours:
            if hour in template["skip"]:
                continue
            h, m = (int(part) for part in hour.split(":"))
            slots.append(
                Slot(
                    id=f"{current.year}{current.month}{current.day}-{hour}",
                    starts_at=datetime(current.year, current.month, current.day, h, m),
                    availability=SlotAvailability.blocked
                    if hour in template["blocked"]
                    else SlotAvailability.open,
                )
            )
    return slots


class Store:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.sessions: list[Session] = [_session(row) for row in _read("sessions")]
        self.slots: list[Slot] = _slots()
        self.patients: list[Patient] = [_patient(row) for row in _read("patients")]
        self.notes: list[Note] = [_note(row) for row in _read("notes")]
        self.complaints: list[Complaint] = [
            _complaint(row) for row in _read("complaints")
        ]
        self.profile: Profile = _profile(_read("profile"))
        self.available: bool = True


store = Store()


def get_store() -> Store:
    return store

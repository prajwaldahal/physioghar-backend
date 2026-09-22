from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import (
    ComplaintCategory,
    ComplaintStatus,
    Gender,
    SessionLocation,
    SessionStatus,
    SlotAvailability,
    SlotState,
)


class Session(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    id: str
    patient_id: str = Field(serialization_alias="patientId")
    patient_name: str = Field(serialization_alias="patientName")
    treatment: str
    location: SessionLocation
    starts_at: datetime = Field(serialization_alias="startsAt")
    status: SessionStatus
    remarks: str | None = None


class Slot(BaseModel):
    id: str
    starts_at: datetime = Field(serialization_alias="startsAt")
    availability: SlotAvailability


class ResolvedSlot(BaseModel):
    id: str
    starts_at: datetime = Field(serialization_alias="startsAt")
    state: SlotState
    session: Session | None = None


class Patient(BaseModel):
    id: str
    name: str
    age: int
    gender: Gender
    phone: str
    condition: str
    treatment_history: list[str] = Field(serialization_alias="treatmentHistory")


class PatientDetail(Patient):
    last_session_at: datetime | None = Field(
        default=None, serialization_alias="lastSessionAt"
    )
    previous_sessions: list[Session] = Field(
        default_factory=list, serialization_alias="previousSessions"
    )


class Note(BaseModel):
    id: str
    patient_id: str = Field(serialization_alias="patientId")
    note: str
    exercises: list[str]
    next_session_plan: str | None = Field(
        default=None, serialization_alias="nextSessionPlan"
    )
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime | None = Field(
        default=None, serialization_alias="updatedAt"
    )


class Profile(BaseModel):
    name: str
    email: str
    phone: str
    experience_years: int = Field(serialization_alias="experienceYears")
    specialization: str
    address: str


class Complaint(BaseModel):
    id: str
    reference: str
    category: ComplaintCategory
    subject: str
    description: str
    status: ComplaintStatus
    created_at: datetime = Field(serialization_alias="createdAt")


class AvailabilityStatus(BaseModel):
    available: bool

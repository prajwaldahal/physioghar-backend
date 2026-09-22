from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ComplaintCategory


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    email: str = Field(pattern=r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    phone: str = Field(pattern=r"^\d{10}$")
    experience_years: int = Field(ge=0, le=60, alias="experienceYears")
    specialization: str = Field(min_length=1)
    address: str = Field(min_length=1)


class AvailabilityUpdate(BaseModel):
    available: bool


class SlotCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    starts_at: str = Field(alias="startsAt")


class CompleteSession(BaseModel):
    remarks: str | None = Field(default=None, max_length=300)


class RescheduleSession(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    starts_at: str = Field(alias="startsAt")


class NoteCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    patient_id: str = Field(alias="patientId")
    note: str = Field(min_length=1, max_length=400)
    exercises: list[str] = Field(default_factory=list)
    next_session_plan: str | None = Field(
        default=None, max_length=200, alias="nextSessionPlan"
    )


class NoteUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note: str = Field(min_length=1, max_length=400)
    exercises: list[str] = Field(default_factory=list)
    next_session_plan: str | None = Field(
        default=None, max_length=200, alias="nextSessionPlan"
    )


class ComplaintCreate(BaseModel):
    category: ComplaintCategory
    subject: str = Field(min_length=5, max_length=80)
    description: str = Field(min_length=20, max_length=500)

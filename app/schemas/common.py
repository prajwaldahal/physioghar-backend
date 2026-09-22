from enum import Enum


class SessionStatus(str, Enum):
    pending = "pending"
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"
    declined = "declined"


class SessionLocation(str, Enum):
    home_visit = "homeVisit"
    clinic = "clinic"


class SlotAvailability(str, Enum):
    open = "open"
    blocked = "blocked"


class SlotState(str, Enum):
    open = "open"
    booked = "booked"
    blocked = "blocked"


class Gender(str, Enum):
    female = "female"
    male = "male"
    other = "other"


class ComplaintCategory(str, Enum):
    patient_issue = "patientIssue"
    booking_issue = "bookingIssue"
    payment_issue = "paymentIssue"
    technical_issue = "technicalIssue"
    other = "other"


class ComplaintStatus(str, Enum):
    open = "open"
    resolved = "resolved"


HOLDS_SLOT = {SessionStatus.upcoming, SessionStatus.completed}

import random
from datetime import datetime

from app.repositories.store import Store
from app.schemas.common import ComplaintCategory, ComplaintStatus
from app.schemas.models import Complaint


def list_complaints(store: Store) -> list[Complaint]:
    return sorted(store.complaints, key=lambda c: c.created_at, reverse=True)


def create_complaint(
    store: Store,
    category: ComplaintCategory,
    subject: str,
    description: str,
) -> Complaint:
    created = Complaint(
        id=f"complaint-{int(datetime.now().timestamp() * 1_000_000)}",
        reference=f"PG-{random.randint(10000, 99999)}",
        category=category,
        subject=subject.strip(),
        description=description.strip(),
        status=ComplaintStatus.open,
        created_at=datetime.now(),
    )
    store.complaints.insert(0, created)
    return created

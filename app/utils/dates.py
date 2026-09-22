from datetime import date, datetime, timedelta

SLOT_MINUTES = 60


def resolve_date(day_offset: int, time_of_day: str) -> datetime:
    hour, minute = (int(part) for part in time_of_day.split(":"))
    today = datetime.now()
    return datetime(today.year, today.month, today.day, hour, minute) + timedelta(
        days=day_offset
    )


def date_only(value: datetime) -> date:
    return value.date()


def start_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday())


def slot_end(start: datetime) -> datetime:
    return start + timedelta(minutes=SLOT_MINUTES)


def overlaps(first: datetime, second: datetime) -> bool:
    return first < slot_end(second) and second < slot_end(first)

import datetime


def to_human_time(tm: datetime.time) -> str:
    return tm.strftime('%H:%M')


def from_human_time(tm: str) -> datetime.time:
    return datetime.time.fromisoformat(tm)

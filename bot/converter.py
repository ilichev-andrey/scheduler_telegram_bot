import datetime


def to_human_time(tm: datetime.time) -> str:
    return tm.strftime('%H:%M')

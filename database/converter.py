from datetime import datetime


def to_human_time(dt: datetime) -> str:
    return '{:02d}:{:02d}'.format(dt.hour, dt.minute)

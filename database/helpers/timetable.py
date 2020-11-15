from datetime import time
from typing import List

from database.containers import TimetableEntry
from database.exceptions import TimetableEntryIsNotFound


def __is_equal_time(tm1: time, tm2: time):
    if tm1.hour != tm2.hour:
        return False

    return tm1.minute == tm2.minute


def get_by_day_time(timetable: List[TimetableEntry], day_time: time) -> TimetableEntry:
    for entry in timetable:
        if __is_equal_time(day_time, entry.start_dt.time()):
            return entry

    raise TimetableEntryIsNotFound('Не найдена запись в расписании')

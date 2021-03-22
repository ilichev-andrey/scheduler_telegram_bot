import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

_DATE_TIME_DELIMITER = ' '
_TIME_FORMAT = '%H:%M'
_DATE_TIME_FORMAT = '%d.%m.%Y'
_DATE_TIME_WEEK_DAY_FORMAT = f'{_DATE_TIME_FORMAT} (%A)'


def to_human_time(tm: datetime.time) -> str:
    return tm.strftime(_TIME_FORMAT)


def from_human_time(tm: str) -> datetime.time:
    """
    :raises
        ValueError если некорректный формат даты
    """
    return datetime.time.fromisoformat(tm)


def to_human_date(dt: datetime.date) -> str:
    return f'{dt.strftime(_DATE_TIME_WEEK_DAY_FORMAT)}'


def from_human_date(dt: str) -> datetime.date:
    """
    :raises
        ValueError если некорректный формат даты
    """
    pos = dt.find('(')
    dt = dt[:pos].strip()
    return datetime.datetime.strptime(dt, _DATE_TIME_FORMAT)


def to_human_datetime(dt: datetime.datetime) -> str:
    return f'{to_human_time(dt.time())}{_DATE_TIME_DELIMITER}{dt.strftime(_DATE_TIME_WEEK_DAY_FORMAT)}'


def from_human_datetime(dt: str) -> datetime.datetime:
    """
    :raises
        ValueError если некорректный формат даты
    """
    pos = dt.find('(')
    dt = dt[:pos].strip()
    return datetime.datetime.strptime(dt, f'{_TIME_FORMAT} {_DATE_TIME_FORMAT}')

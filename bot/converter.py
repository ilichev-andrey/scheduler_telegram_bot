import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

_DATE_TIME_DELIMITER = ' '


def to_human_time(tm: datetime.time) -> str:
    return tm.strftime('%H:%M')


def from_human_time(tm: str) -> datetime.time:
    """
    :raises
        ValueError если некорректный формат даты
    """
    return datetime.time.fromisoformat(tm)


def to_human_date(dt: datetime.date) -> str:
    return f'{dt.strftime("%d.%m.%y (%A)")}'


def from_human_date(dt: str) -> datetime.date:
    """
    :raises
        ValueError если некорректный формат даты
    """
    pos = dt.find('(')
    dt = dt[:pos].strip()
    return datetime.datetime.strptime(dt, '%d.%m.%y')


def to_human_datetime(dt: datetime.datetime) -> str:
    return f'{to_human_time(dt.time())}{_DATE_TIME_DELIMITER}{dt.strftime("%d.%m.%y (%A)")}'


def from_human_datetime(dt: str) -> datetime.datetime:
    """
    :raises
        ValueError если некорректный формат даты
    """
    pos = dt.find('(')
    dt = dt[:pos].strip()
    return datetime.datetime.strptime(dt, '%H:%M %d.%m.%y')

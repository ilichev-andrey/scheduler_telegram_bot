from datetime import datetime
from typing import NamedTuple, Dict, Any

from bot.enums import UserType


class User(NamedTuple):
    id: int
    type: UserType
    first_name: str
    last_name: str
    username: str

    def asdict(self) -> Dict[str, Any]:
        fields = self._asdict()
        fields['type'] = self.type.value
        return fields


def make_user(**kwargs) -> User:
    return User(type=UserType(kwargs.pop('type')), **kwargs)


class Service(NamedTuple):
    id: int
    name: str
    time_interval: int

    def asdict(self) -> Dict[str, Any]:
        return self._asdict()


def make_service(**kwargs) -> Service:
    return Service(**kwargs)


class TimetableEntry(NamedTuple):
    id: int
    worker_id: int
    client_id: int or None
    service_id: int or None
    create_dt: datetime
    start_dt: datetime


def make_timetable_entry(**kwargs) -> TimetableEntry:
    return TimetableEntry(
        create_dt=datetime.fromtimestamp(kwargs.pop('create_dt')),
        start_dt=datetime.fromtimestamp(kwargs.pop('start_dt')),
        **kwargs)

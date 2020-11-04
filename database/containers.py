from typing import NamedTuple

from bot.enums import UserType


class User(NamedTuple):
    id: int
    type: UserType

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


def make_user(**kwargs):
    return User(type=UserType(kwargs.pop('type')), **kwargs)

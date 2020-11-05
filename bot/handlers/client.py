from typing import Tuple

from bot.enums import UserType
from bot.handlers.user import User
from bot.view.buttons import Buttons


class Client(User):
    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value
        )

    def get_user_type(self):
        return UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value

from typing import Tuple

from bot.enums import UserType
from bot.handlers import User
from bot.view import Buttons


class Worker(User):
    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE.value)

    def get_user_type(self):
        return UserType.WORKER

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE.value, Buttons.WORKER_ADD_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE_TODAY.value, Buttons.WORKER_TIMETABLE_WEEK.value

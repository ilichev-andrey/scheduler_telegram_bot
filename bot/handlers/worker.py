from typing import Tuple

from bot.enums import UserType

from bot.handlers.user import User


class Worker(User):
    TIMETABLE_DISPLAY_BUTTON = 'Показать расписание'

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == self.TIMETABLE_DISPLAY_BUTTON
        )

    def get_user_type(self):
        return UserType.WORKER

    def get_main_buttons(self) -> Tuple[str, ...]:
        return 'Показать расписание', 'Записать'

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return 'На сегодня', 'На неделю'

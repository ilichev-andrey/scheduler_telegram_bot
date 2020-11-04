from typing import Tuple

from bot.enums import UserType
from bot.handlers.user import User


class Client(User):
    TIMETABLE_DISPLAY_BUTTON = 'Показать  мои записи'

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == self.TIMETABLE_DISPLAY_BUTTON
        )

    def get_user_type(self):
        return UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return 'Показать мои записи', 'Записаться'

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return 'Будущие записи', 'История записей'

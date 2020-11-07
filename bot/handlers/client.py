from typing import Tuple

from aiogram import Dispatcher, types

from bot.enums import UserType
from bot.handlers import calendar, user
from bot.view.buttons import Buttons


class Client(user.User):
    def __init__(self, dispatcher: Dispatcher, calendar_handler: calendar.Calendar):
        super().__init__(dispatcher)
        self.calendar = calendar_handler

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value)
        self.dispatcher.register_message_handler(
            self._add_timetable_entry,
            lambda message: message.text == Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value)

    def get_user_type(self):
        return UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value

    async def _add_timetable_entry(self, message: types.Message):
        await self.calendar.open(message)

from typing import Tuple

from aiogram import Dispatcher

from bot.enums import UserType
from bot.handlers import calendar, user
from bot.handlers.client import sign_up
from bot.view.buttons import Buttons
from database.db import DB


class Client(user.User):
    def __init__(self, dispatcher: Dispatcher, db: DB, calendar_handler: calendar.Calendar):
        super().__init__(dispatcher)
        self.db = db
        self.calendar = calendar_handler
        self.sign_up = sign_up.SignUp(self.dispatcher, self.db, self.calendar)

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value)
        self.sign_up.init()

    def get_user_type(self):
        return UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value

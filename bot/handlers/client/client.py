from typing import Tuple

from aiogram import Dispatcher

from bot.enums import UserType
from bot.handlers import Calendar, User, client
from bot.view.buttons import Buttons
from database import DB, provider


class Client(User):
    def __init__(self, dispatcher: Dispatcher, db: DB, service_provider: provider.Service, calendar_handler: Calendar):
        super().__init__(dispatcher)

        self.timetable_provider = provider.ClientTimetable(db)
        self.calendar = calendar_handler
        self.sign_up = client.SignUp(dispatcher, service_provider, self.timetable_provider, calendar_handler)

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

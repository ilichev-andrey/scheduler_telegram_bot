from typing import Tuple

from aiogram import Dispatcher
from scheduler_core import enums

from handlers.user import User
from handlers.worker.services import Services
from view.buttons import Buttons


class Worker(User):
    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher)
        self.services = Services(dispatcher)

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE.value)
        self.services.init()

    def get_user_type(self):
        return enums.UserType.WORKER

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE.value, Buttons.WORKER_ADD_TIMETABLE_ENTRY.value, Buttons.WORKER_SERVICES.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE_TODAY.value, Buttons.WORKER_TIMETABLE_WEEK.value

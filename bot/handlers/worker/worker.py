from typing import Tuple

from aiogram import Dispatcher, types

from handlers import states
from handlers.user import User
from handlers.worker.services import Services
from view import static, keyboard
from view.buttons import Buttons


class Worker(User):
    _services: Services

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher)
        self._services = Services(dispatcher)

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._show_timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE.value,
            state=states.BotStates.worker_page.main_page
        )
        # self._services.init()

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE.value, Buttons.WORKER_ADD_TIMETABLE_ENTRY.value, Buttons.WORKER_SERVICES.value

    @staticmethod
    async def _show_timetable(message: types.Message):
        await states.ClientStates.timetable_page.set()
        button_names = (Buttons.WORKER_TIMETABLE_TODAY.value, Buttons.WORKER_TIMETABLE_WEEK.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names, one_time_keyboard=False)
        )

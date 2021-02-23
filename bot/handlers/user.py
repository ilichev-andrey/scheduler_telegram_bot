from abc import abstractmethod
from typing import Tuple

from handlers.abstract_handler import AbstractHandler


class User(AbstractHandler):
    @abstractmethod
    def get_main_buttons(self) -> Tuple[str, ...]:
        pass

    # async def _timetable(self, message: types.Message):
    #     reply_markup = keyboard.create_reply_keyboard_markup(self.get_timetable_buttons())
    #     await states.ClientStates.timetable_page.set()
    #     await message.answer(static.SELECT_ITEM, reply_markup=reply_markup)

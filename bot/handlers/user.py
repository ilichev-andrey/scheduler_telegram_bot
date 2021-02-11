from abc import abstractmethod
from typing import Tuple

from aiogram import types

from handlers.abstract_handler import AbstractHandler
from view import keyboard, static


class User(AbstractHandler):
    @abstractmethod
    def get_user_type(self):
        pass

    @abstractmethod
    def get_main_buttons(self) -> Tuple[str, ...]:
        pass

    @abstractmethod
    def get_timetable_buttons(self) -> Tuple[str, ...]:
        pass

    async def _timetable(self, message: types.Message):
        reply_markup = keyboard.create_reply_keyboard_markup(self.get_timetable_buttons())
        await message.answer(static.SELECT_ITEM, reply_markup=reply_markup)

from abc import ABC, abstractmethod
from typing import Tuple

from aiogram import Dispatcher, types

import bot.view.keyboard as keyboard


class User(ABC):
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher

    @abstractmethod
    def init(self) -> None:
        pass

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
        await message.answer('Выберите пункт:', reply_markup=reply_markup)

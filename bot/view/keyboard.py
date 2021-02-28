from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from view.buttons import Buttons


def create_reply_keyboard_markup(button_names: Iterable = (), with_complete: bool = True, with_home: bool = True,
                                 one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    for button_name in button_names:
        poll_keyboard.add(KeyboardButton(text=button_name))

    service_buttons = []
    if with_home:
        service_buttons.append(KeyboardButton(text=Buttons.BACK_TO_HOME.value))

    if with_complete:
        service_buttons.append(KeyboardButton(text=Buttons.COMPLETE.value))

    poll_keyboard.row(*service_buttons)
    return poll_keyboard

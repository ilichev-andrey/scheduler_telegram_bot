from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from view.buttons import Buttons


def create_reply_keyboard_markup(button_names: Iterable, with_cancel: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button_name in button_names:
        poll_keyboard.add(KeyboardButton(text=button_name))

    if with_cancel:
        poll_keyboard.add(Buttons.CANCEL.value)
    return poll_keyboard

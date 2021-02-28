from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from view import static
from view.buttons import Buttons


def _add_service_buttons(keyboard: ReplyKeyboardMarkup, with_complete: bool = True,
                         with_home: bool = True) -> ReplyKeyboardMarkup:
    service_buttons = []
    if with_home:
        service_buttons.append(KeyboardButton(text=Buttons.BACK_TO_HOME.value))

    if with_complete:
        service_buttons.append(KeyboardButton(text=Buttons.COMPLETE.value))

    keyboard.row(*service_buttons)
    return keyboard


def create_reply_keyboard_markup(button_names: Iterable = (), with_complete: bool = True, with_home: bool = True,
                                 one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    for button_name in button_names:
        poll_keyboard.add(KeyboardButton(text=button_name))

    return _add_service_buttons(poll_keyboard, with_complete=with_complete, with_home=with_home)


def create_info_keyboard_markup(request_contact: bool = False, request_location: bool = False,
                                with_complete: bool = True, with_home: bool = True,
                                one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    if request_contact:
        poll_keyboard.add(KeyboardButton(static.SEND_PHONE_NUMBER, request_contact=True))

    if request_location:
        poll_keyboard.add(KeyboardButton(static.SEND_LOCATION, request_location=True))

    return _add_service_buttons(poll_keyboard, with_complete=with_complete, with_home=with_home)

from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from view import static
from view.buttons import Buttons


def add_service_buttons_for_reply_keyboard(keyboard: ReplyKeyboardMarkup, with_complete: bool = True,
                                           with_home: bool = True) -> ReplyKeyboardMarkup:
    service_buttons = []
    if with_home:
        service_buttons.append(KeyboardButton(text=Buttons.BACK_TO_HOME.value))

    if with_complete:
        service_buttons.append(KeyboardButton(text=Buttons.COMPLETE.value))

    keyboard.row(*service_buttons)
    return keyboard


def add_service_buttons_for_inline_keyboard(keyboard: InlineKeyboardMarkup, with_complete: bool = True,
                                            with_home: bool = True) -> InlineKeyboardMarkup:
    service_buttons = []
    if with_home:
        button = Buttons.BACK_TO_HOME.value
        service_buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    if with_complete:
        button = Buttons.COMPLETE.value
        service_buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    keyboard.row(*service_buttons)
    return keyboard


def create_reply_keyboard_markup(button_names: Iterable = (), with_complete: bool = True, with_home: bool = True,
                                 one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    for button_name in button_names:
        poll_keyboard.add(KeyboardButton(text=button_name))

    return add_service_buttons_for_reply_keyboard(poll_keyboard, with_complete=with_complete, with_home=with_home)


def create_info_keyboard_markup(request_contact: bool = False, request_location: bool = False,
                                with_complete: bool = True, with_home: bool = True,
                                one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    if request_contact:
        poll_keyboard.add(KeyboardButton(static.SEND_PHONE_NUMBER, request_contact=True))

    if request_location:
        poll_keyboard.add(KeyboardButton(static.SEND_LOCATION, request_location=True))

    return add_service_buttons_for_reply_keyboard(poll_keyboard, with_complete=with_complete, with_home=with_home)

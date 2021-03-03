from datetime import datetime
from typing import Tuple, List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from scheduler_core import containers, enums
from wrappers import LoggerWrap

import exceptions
from handlers import states, handler
from handlers.calendar import Calendar
from handlers.client.sign_up import SignUp
from handlers.user import User
from managers.service import ServiceManager
from managers.timetable import TimetableManager
from managers.user import UserManager
from view import keyboard, static
from view.buttons import Buttons


class Client(User):
    _service_manager: ServiceManager
    _timetable_manager: TimetableManager
    _calendar: Calendar
    _sign_up: SignUp

    def __init__(self, dispatcher: Dispatcher, service_manager: ServiceManager, timetable_manager: TimetableManager,
                 user_manager: UserManager, calendar_handler: Calendar):
        super().__init__(dispatcher)
        self._service_manager = service_manager
        self._timetable_manager = timetable_manager
        self._calendar = calendar_handler
        self._sign_up = SignUp(dispatcher, service_manager, timetable_manager, user_manager, calendar_handler)

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._show_timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value,
            state=states.BotStates.client_page.main_page,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._show_timetable_future,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE_FUTURE.value,
            state=states.BotStates.client_page.timetable_page,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._show_timetable_history,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE_HISTORY.value,
            state=states.BotStates.client_page.timetable_page,
            content_types=types.ContentTypes.TEXT
        )
        self._sign_up.init()

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    async def _show_timetable_future(self, message: types.Message, state: FSMContext):
        user = await handler.get_user(state)
        try:
            entries = await self._timetable_manager.get_client_timetable(user.id)
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        entries = self._get_future_entries(entries)
        time_type = enums.TimeType.FUTURE
        if not entries:
            await message.answer(static.get_client_timetable_title(time_type, is_found=False))
            return

        entries.sort(key=lambda entry: entry.start_dt)
        button_names_gen = (self._get_button_name(entry) for entry in entries)

        markup = InlineKeyboardMarkup()
        for button_name in button_names_gen:
            markup.add(InlineKeyboardButton(button_name, callback_data='button'))

        await message.answer(static.get_client_timetable_title(time_type), reply_markup=markup)

    async def _show_timetable_history(self, message: types.Message, state: FSMContext):
        user = await handler.get_user(state)
        try:
            entries = await self._timetable_manager.get_client_timetable(user.id)
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        entries = self._get_past_entries(entries)
        time_type = enums.TimeType.PAST
        if not entries:
            await message.answer(static.get_client_timetable_title(time_type, is_found=False))
            return

        entries.sort(key=lambda entry: entry.start_dt)
        button_names_gen = (self._get_button_name(entry) for entry in entries)

        markup = InlineKeyboardMarkup()
        for button_name in button_names_gen:
            markup.add(InlineKeyboardButton(button_name, callback_data='button'))

        await message.answer(static.get_client_timetable_title(time_type), reply_markup=markup)

    @staticmethod
    async def _show_timetable(message: types.Message):
        await states.ClientStates.timetable_page.set()
        button_names = (Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names, one_time_keyboard=False),
        )

    @staticmethod
    def _get_future_entries(entries: List[containers.TimetableEntry]) -> List[containers.TimetableEntry]:
        now = datetime.today()
        return [entry for entry in entries if entry.start_dt >= now]

    @staticmethod
    def _get_past_entries(entries: List[containers.TimetableEntry]) -> List[containers.TimetableEntry]:
        now = datetime.today()
        return [entry for entry in entries if entry.start_dt < now]

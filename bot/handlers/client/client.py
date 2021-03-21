from datetime import datetime
from typing import Tuple, List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from scheduler_core import containers, enums
from wrappers import LoggerWrap

from bot import exceptions
from bot.handlers import states, handler
from bot.handlers.calendar import Calendar
from bot.handlers.client.sign_up import ClientSignUp
from bot.handlers.user import User
from bot.managers.service import ServiceManager
from bot.managers.timetable import TimetableManager
from bot.managers.user import UserManager
from bot.view import keyboard, static
from bot.view.buttons import Buttons


class Client(User):
    _SHOW_DETAIL_BUTTON_PREFIX = 'detail_entry_btn_'
    _EDIT_ENTRY_BUTTON_PREFIX = 'edit_entry_btn_'
    _RELEASE_SLOT_BUTTON_PREFIX = 'release_slot_btn_'

    _service_manager: ServiceManager
    _timetable_manager: TimetableManager
    _calendar: Calendar
    _sign_up: ClientSignUp

    def __init__(self, dispatcher: Dispatcher, service_manager: ServiceManager, timetable_manager: TimetableManager,
                 user_manager: UserManager, calendar_handler: Calendar):
        super().__init__(dispatcher)
        self._service_manager = service_manager
        self._timetable_manager = timetable_manager
        self._calendar = calendar_handler
        self._sign_up = ClientSignUp(dispatcher, service_manager, timetable_manager, user_manager, calendar_handler)

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
        self._dispatcher.register_callback_query_handler(
            self._timetable_future_callback_query,
            lambda callback_query: (callback_query.data and
                                    callback_query.data.startswith(self._EDIT_ENTRY_BUTTON_PREFIX)),
            state=states.BotStates.client_page.future_visits
        )
        self._dispatcher.register_callback_query_handler(
            self._release_slot_callback_query,
            lambda callback_query: (callback_query.data and
                                    callback_query.data.startswith(self._RELEASE_SLOT_BUTTON_PREFIX)),
            state=states.BotStates.client_page.future_visits
        )
        self._dispatcher.register_message_handler(
            self._show_timetable_history,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE_HISTORY.value,
            state=states.BotStates.client_page.timetable_page,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_callback_query_handler(
            self._timetable_history_callback_query,
            lambda callback_query: (callback_query.data and
                                    callback_query.data.startswith(self._SHOW_DETAIL_BUTTON_PREFIX)),
            state=states.BotStates.client_page.visit_history
        )
        self._sign_up.init()

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    async def _show_timetable_future(self, message: types.Message, state: FSMContext):
        user = await handler.get_user(state)
        try:
            entries = await self._timetable_manager.get_client_timetable(user.id)
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        entries = self._get_future_entries(entries)
        time_type = enums.TimeType.FUTURE
        if not entries:
            await message.answer(static.get_client_timetable_title(time_type, is_found=False))
            return

        entries.sort(key=lambda entry: entry.start_dt)
        await state.update_data(data={'entries': {entry.id: entry for entry in entries}})

        markup = InlineKeyboardMarkup()
        for _entry in entries:
            markup.add(InlineKeyboardButton(
                text=self._get_button_name(_entry),
                callback_data=f'{self._EDIT_ENTRY_BUTTON_PREFIX}{_entry.id}')
            )

        await states.BotStates.client_page.future_visits.set()
        await message.answer(static.get_client_timetable_title(time_type), reply_markup=markup)

    async def _timetable_future_callback_query(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()
        user_data = await state.get_data()

        entry_id = int(query.data.removeprefix(self._EDIT_ENTRY_BUTTON_PREFIX))
        await message.answer(
            static.get_detail_client_timetable(user_data['entries'][entry_id]),
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                text='Отменить запись',
                callback_data=f'{self._RELEASE_SLOT_BUTTON_PREFIX}{entry_id}')
            )
        )

    async def _release_slot_callback_query(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()

        entry_id = int(query.data.removeprefix(self._RELEASE_SLOT_BUTTON_PREFIX))
        try:
            entries = await self._timetable_manager.release_slots(frozenset((entry_id,)))
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        if entries:
            await message.answer(static.get_detail_release_client_timetable(entries[0]))

    async def _show_timetable_history(self, message: types.Message, state: FSMContext):
        await message.answer(static.EMPTY_TEXT, reply_markup=keyboard.create_reply_keyboard_markup())

        user = await handler.get_user(state)
        try:
            entries = await self._timetable_manager.get_client_timetable(user.id)
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        entries = self._get_past_entries(entries)
        time_type = enums.TimeType.PAST
        if not entries:
            await message.answer(static.get_client_timetable_title(time_type, is_found=False))
            return

        entries.sort(key=lambda entry: entry.start_dt)
        await state.update_data(data={'entries': {entry.id: entry for entry in entries}})

        markup = InlineKeyboardMarkup()
        for _entry in entries:
            markup.add(InlineKeyboardButton(
                text=self._get_button_name(_entry),
                callback_data=f'{self._SHOW_DETAIL_BUTTON_PREFIX}{_entry.id}')
            )

        await states.BotStates.client_page.visit_history.set()
        await message.answer(static.get_client_timetable_title(time_type), reply_markup=markup)

    async def _timetable_history_callback_query(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()
        user_data = await state.get_data()

        entry_id = int(query.data.removeprefix(self._SHOW_DETAIL_BUTTON_PREFIX))
        await message.answer(static.get_detail_client_timetable(user_data['entries'][entry_id]))

    @staticmethod
    async def _show_timetable(message: types.Message):
        await states.ClientStates.timetable_page.set()
        button_names = (Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names),
        )

    @staticmethod
    def _get_future_entries(entries: List[containers.TimetableEntry]) -> List[containers.TimetableEntry]:
        now = datetime.today()
        return [entry for entry in entries if entry.start_dt >= now]

    @staticmethod
    def _get_past_entries(entries: List[containers.TimetableEntry]) -> List[containers.TimetableEntry]:
        now = datetime.today()
        return [entry for entry in entries if entry.start_dt < now]

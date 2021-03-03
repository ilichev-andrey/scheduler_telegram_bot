from typing import Tuple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from scheduler_core import enums
from wrappers import LoggerWrap

import exceptions
from handlers import states, handler
from handlers.user import User
from handlers.worker.services import Services
from managers.timetable import TimetableManager
from view import static, keyboard
from view.buttons import Buttons


class Worker(User):
    _timetable_manager: TimetableManager
    _services: Services

    def __init__(self, dispatcher: Dispatcher, timetable_manager: TimetableManager):
        super().__init__(dispatcher)
        self._timetable_manager = timetable_manager
        self._services = Services(dispatcher)

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._show_timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE.value,
            state=states.BotStates.worker_page.main_page
        )
        self._dispatcher.register_message_handler(
            self._show_today_timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE_TODAY.value,
            state=states.BotStates.worker_page.timetable_page,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._show_week_timetable,
            lambda message: message.text == Buttons.WORKER_TIMETABLE_WEEK.value,
            state=states.BotStates.worker_page.timetable_page,
            content_types=types.ContentTypes.TEXT
        )
        # self._services.init()

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.WORKER_TIMETABLE.value, Buttons.WORKER_ADD_TIMETABLE_ENTRY.value, Buttons.WORKER_SERVICES.value

    @staticmethod
    async def _show_timetable(message: types.Message):
        await states.WorkerStates.timetable_page.set()
        button_names = (Buttons.WORKER_TIMETABLE_TODAY.value, Buttons.WORKER_TIMETABLE_WEEK.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names, one_time_keyboard=False)
        )

    async def _show_today_timetable(self, message: types.Message, state: FSMContext):
        await self._show_timetable_by_type(message, state, enums.TimeType.FUTURE, enums.TimeLimit.DAY)

    async def _show_week_timetable(self, message: types.Message, state: FSMContext):
        await self._show_timetable_by_type(message, state, enums.TimeType.FUTURE, enums.TimeLimit.WEEK)

    async def _show_timetable_by_type(self, message: types.Message, state: FSMContext, time_type: enums.TimeType,
                                      time_limit: enums.TimeLimit):
        user = await handler.get_user(state)
        try:
            entries = await self._timetable_manager.get_worker_timetable(user.id, time_type, time_limit)
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return
        except exceptions.EmptyTimetable:
            entries = []

        if not entries:
            await message.answer(static.get_worker_timetable_title(time_type, time_limit, is_found=False))
            return

        entries.sort(key=lambda entry: entry.start_dt)
        button_names_gen = (self._get_button_name(entry) for entry in entries)

        markup = InlineKeyboardMarkup()
        for button_name in button_names_gen:
            markup.add(InlineKeyboardButton(button_name, callback_data='button'))

        await message.answer(static.get_worker_timetable_title(time_type, time_limit), reply_markup=markup)


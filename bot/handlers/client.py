from datetime import time
from typing import Tuple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot import exceptions
from bot.enums import UserType
from bot.handlers import calendar, user
from bot.handlers.states import ClientRequestStates
from bot.view import keyboard
from bot.view import static
from bot.view.buttons import Buttons
from database import converter
from database.db import DB
from database.helpers import services, timetable
from wrappers.logger import LoggerWrap


class Client(user.User):
    def __init__(self, dispatcher: Dispatcher, db: DB, calendar_handler: calendar.Calendar):
        super().__init__(dispatcher)
        self.db = db
        self.calendar = calendar_handler

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value)
        self.dispatcher.register_message_handler(
            self._select_service,
            lambda message: message.text == Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value,
            state='*')
        self.dispatcher.register_message_handler(
            self._select_date,
            state=ClientRequestStates.waiting_service,
            content_types=types.ContentTypes.TEXT)
        self.dispatcher.register_message_handler(
            self._select_time,
            state=ClientRequestStates.waiting_date,
            content_types=types.ContentTypes.TEXT)
        self.dispatcher.register_message_handler(
            self._add_timetable_entry,
            state=ClientRequestStates.waiting_time,
            content_types=types.ContentTypes.TEXT)

    def get_user_type(self):
        return UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value

    async def _select_service(self, message: types.Message, state: FSMContext):
        try:
            services = self.db.get_services()
        except exceptions.ServiceIsNotFound as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            return

        await state.update_data(services=services)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(tuple(service.name for service in services)))

        await ClientRequestStates.waiting_service.set()

    async def _select_date(self, message: types.Message, state: FSMContext):
        await state.update_data(chosen_service=message.text.lower())
        await message.answer(static.SELECT_DATE)
        await self.calendar.open(
            message,
            on_selected_date=lambda chosen_date: self._on_selected_date(chosen_date, message, state))

    @staticmethod
    async def _on_selected_date(chosen_date: str, message: types.Message, state: FSMContext):
        LoggerWrap().get_logger().info(f'получена дата {chosen_date}')
        await state.update_data(chosen_date=chosen_date)
        await ClientRequestStates.waiting_date.set()

        button_name = f'{static.SELECTED_DATE} {chosen_date}. Нажмите для продолжения'
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup((button_name,)))

    async def _select_time(self, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        try:
            timetable_day = self.db.get_timetable_by_day(user_data['chosen_date'])
        except exceptions.TimetableEntryIsNotFound as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            return

        await state.update_data(timetable_day=timetable_day)
        button_names_gen = (converter.to_human_time(entry.start_dt) for entry in timetable_day)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(tuple(button_names_gen)))

        await ClientRequestStates.waiting_time.set()

    async def _add_timetable_entry(self, message: types.Message, state: FSMContext):
        await state.update_data(chosen_time=message.text.lower())
        user_data = await state.get_data()
        LoggerWrap().get_logger().info(f'Выбраны параметры: {user_data}')

        timetable_entry = timetable.get_by_day_time(
            user_data['timetable_day'],
            time.fromisoformat(user_data['chosen_time']))

        service = services.get_by_name(user_data['services'], user_data['chosen_service'])
        self.db.update_timetable_entry(timetable_entry.id, service.id, message.from_user.id)
        await message.answer(f'{static.ADDED} на услугу {service.name} в {timetable_entry.start_dt}')
        await state.finish()


from datetime import datetime, time
from typing import List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from scheduler_core import containers
from wrappers import LoggerWrap

import converter
import exceptions
from handlers import states, handler
from handlers.abstract_handler import AbstractHandler
from handlers.calendar import Calendar
from managers.service import ServiceManager
from managers.timetable import TimetableManager
from managers.user import UserManager
from view import static, keyboard
from view.buttons import Buttons


class SignUp(AbstractHandler):
    _service_manager: ServiceManager
    _timetable_manager: TimetableManager
    _user_manager: UserManager
    _calendar: Calendar

    def __init__(self, dispatcher: Dispatcher, service_manager: ServiceManager, timetable_manager: TimetableManager,
                 user_manager: UserManager, calendar_handler: Calendar):
        super().__init__(dispatcher)
        self._service_manager = service_manager
        self._timetable_manager = timetable_manager
        self._user_manager = user_manager
        self._calendar = calendar_handler

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._select_service,
            lambda message: message.text == Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value,
            state=states.ClientStates.main_page,
            content_types=types.ContentTypes.TEXT
        )
        self.dispatcher.register_message_handler(
            self._select_date,
            state=states.SignUpStates.select_date,
            content_types=types.ContentTypes.TEXT
        )
        self.dispatcher.register_message_handler(
            self._select_time,
            state=states.SignUpStates.select_time,
            content_types=types.ContentTypes.TEXT
        )
        self.dispatcher.register_message_handler(
            self._add_timetable_entry,
            state=states.SignUpStates.add_timetable_entry,
            content_types=types.ContentTypes.TEXT
        )

    async def _select_worker(self, message: types.Message, state: FSMContext):
        """
        Получает от модуля core первого работника (хардкод, для того чтобы не давать пользователю выбора,
        потому то пока есть только один работник)
        """
        try:
            workers = await self._user_manager.get_workers()
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
        else:
            await state.update_data(data={'worker': workers[0]})

    async def _select_service(self, message: types.Message, state: FSMContext):
        try:
            service_list = await self._service_manager.get()
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        await state.update_data(data={'services': service_list})
        button_names = (service.name for service in service_list)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names)
        )

        await states.SignUpStates.select_date.set()

    async def _select_date(self, message: types.Message, state: FSMContext):
        await self._select_worker(message, state)

        user_data = await state.get_data()

        service = self._get_service_by_name(user_data['services'], message.text.lower())
        await state.update_data(data={'chosen_service': service})
        try:
            entries = await self._timetable_manager.get_free_slots(
                date_ranges=containers.DateRanges(start_dt=datetime.today()),
                services=frozenset((service.id,)),
                worker_id=user_data.get('worker', containers.User).id
            )
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        if not entries:
            await message.answer(static.BUSY)
            return

        await state.update_data(data={'timetable_entries': entries})
        await message.answer(static.SELECT_DATE)
        await self._calendar.open(
            message,
            on_selected_date=lambda chosen_date: self._on_selected_date(chosen_date, message, state),
            include_dates=set(entry.start_dt.date() for entry in entries)
        )

    @staticmethod
    async def _on_selected_date(chosen_date: str, message: types.Message, state: FSMContext):
        LoggerWrap().get_logger().info(f'Получена дата {chosen_date}')
        await state.update_data(data={'chosen_date': chosen_date})
        await states.SignUpStates.select_time.set()

        button_names = (static.get_selected_date_text(chosen_date),)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names)
        )

    async def _select_time(self, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        timetable_day = self._timetable_manager.filter_by_day(user_data['timetable_entries'], user_data['chosen_date'])
        await state.update_data(data={'timetable_day': timetable_day})

        button_names_gen = (converter.to_human_time(entry.start_dt.time()) for entry in timetable_day)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names_gen)
        )

        await states.SignUpStates.add_timetable_entry.set()

    async def _add_timetable_entry(self, message: types.Message, state: FSMContext):
        chosen_time = message.text.lower()
        user_data = await state.get_data()
        LoggerWrap().get_logger().info(f'Выбраны параметры: {user_data}')

        try:
            entry = self._get_timetable_entry_by_time(
                entries=user_data['timetable_day'],
                tm=converter.from_human_time(chosen_time)
            )
        except exceptions.IncorrectData as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        service: containers.Service = user_data['chosen_service']
        user: containers.User = user_data['user']
        try:
            await self._timetable_manager.sign_up_client(
                entry_ids=frozenset((entry.id,)),
                service_ids=frozenset((service.id,)),
                client_id=user.id
            )
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        await message.answer(static.get_successful_registration_text(service.name, entry.start_dt))
        await message.answer(static.SELECT_ITEM, reply_markup=keyboard.create_reply_keyboard_markup())

    @staticmethod
    def _get_timetable_entry_by_time(entries: List[containers.TimetableEntry], tm: time) -> containers.TimetableEntry:
        for entry in entries:
            if entry.start_dt.time() == tm:
                return entry

        raise exceptions.IncorrectData('Не удалось найти слот в расписании указанному по времени'
                                       f'entries={entries}, time={tm}')

    @staticmethod
    def _get_service_by_name(services: List[containers.Service], service_name: str) -> containers.Service:
        for service in services:
            if service.name == service_name:
                return service

        raise exceptions.IncorrectData(f'Не удалось найти услугу по имени. services={services}, '
                                       f'service_name={service_name}')

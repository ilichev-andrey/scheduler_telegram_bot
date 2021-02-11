from datetime import time

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot.handlers import AbstractHandler, Calendar, client
from bot.view import Buttons, keyboard, static
from database import exceptions, provider
from database.converters import converter
from database.helpers import services, timetable
from wrappers import LoggerWrap


class SignUp(AbstractHandler):
    def __init__(self, dispatcher: Dispatcher, service_provider: provider.Service,
                 timetable_provider: provider.ClientTimetable, calendar_handler: Calendar):
        super().__init__(dispatcher)

        self.service_provider = service_provider
        self.timetable_provider = timetable_provider
        self.calendar = calendar_handler

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._select_service,
            lambda message: message.text == Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value,
            state='*')
        self.dispatcher.register_message_handler(
            self._select_date,
            state=client.ClientRequestStates.waiting_service,
            content_types=types.ContentTypes.TEXT)
        self.dispatcher.register_message_handler(
            self._select_time,
            state=client.ClientRequestStates.waiting_date,
            content_types=types.ContentTypes.TEXT)
        self.dispatcher.register_message_handler(
            self._add_timetable_entry,
            state=client.ClientRequestStates.waiting_time,
            content_types=types.ContentTypes.TEXT)
        self.dispatcher.register_message_handler(
            self._cancel,
            lambda message: message.text == Buttons.CANCEL.value,
            state=client.ClientRequestStates.all_states,
            content_types=types.ContentTypes.TEXT)

    async def _error(self, e: exceptions.BaseBotException, message: types.Message, state: FSMContext):
        LoggerWrap().get_logger().exception(e)
        await self._cancel(message, state)
        await message.answer(static.INTERNAL_ERROR)

    @staticmethod
    async def _cancel(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.answer(static.START, reply_markup=types.ReplyKeyboardRemove())

    async def _select_service(self, message: types.Message, state: FSMContext):
        try:
            service_list = self.service_provider.get()
        except exceptions.ServiceIsNotFound as e:
            await self._error(e, message, state)
            return

        await state.update_data(services=service_list)
        button_names = (*(service.name for service in service_list), Buttons.CANCEL.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names))

        await client.ClientRequestStates.waiting_service.set()

    async def _select_date(self, message: types.Message, state: FSMContext):
        await state.update_data(chosen_service=message.text.lower())

        try:
            entries = self.timetable_provider.get()
        except exceptions.TimetableEntryIsNotFound:
            await message.answer(static.BUSY)
            await self._cancel(message, state)
            return

        await message.answer(static.SELECT_DATE)
        await self.calendar.open(
            message,
            on_selected_date=lambda chosen_date: self._on_selected_date(chosen_date, message, state),
            include_dates=set(entry.start_dt.date() for entry in entries))

    @staticmethod
    async def _on_selected_date(chosen_date: str, message: types.Message, state: FSMContext):
        LoggerWrap().get_logger().info(f'получена дата {chosen_date}')
        await state.update_data(chosen_date=chosen_date)
        await client.ClientRequestStates.waiting_date.set()

        button_names = (f'{static.SELECTED_DATE} {chosen_date}. {static.CLICK_TO_CONTINUE}', Buttons.CANCEL.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names))

    async def _select_time(self, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        try:
            timetable_day = self.timetable_provider.get_by_day(user_data['chosen_date'])
        except exceptions.TimetableEntryIsNotFound as e:
            await self._error(e, message, state)
            return

        await state.update_data(timetable_day=timetable_day)
        times_gen = (converter.to_human_time(entry.start_dt.time()) for entry in timetable_day)
        button_names = (*times_gen, Buttons.CANCEL.value)
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(button_names))

        await client.ClientRequestStates.waiting_time.set()

    async def _add_timetable_entry(self, message: types.Message, state: FSMContext):
        chosen_time = message.text.lower()
        user_data = await state.get_data()
        LoggerWrap().get_logger().info(f'Выбраны параметры: {user_data}')

        timetable_entry = timetable.get_by_day_time(user_data['timetable_day'], time.fromisoformat(chosen_time))

        service = services.get_by_name(user_data['services'], user_data['chosen_service'])
        self.timetable_provider.update_entry(timetable_entry.id, service.id, message.from_user.id)
        await message.answer(f'{static.ADDED} на услугу {service.name} в {timetable_entry.start_dt}')
        await state.finish()

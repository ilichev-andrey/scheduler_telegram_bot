from typing import Tuple, List

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from scheduler_core import containers, enums

from handlers.calendar import Calendar
from handlers.client.sign_up import SignUp
from handlers.user import User
from view import keyboard
from view.buttons import Buttons


class ClientRequestStates(StatesGroup):
    waiting_service = State()
    waiting_date = State()
    waiting_time = State()
    cancel = State()


class Client(User):
    def __init__(self, dispatcher: Dispatcher, calendar_handler: Calendar):
        super().__init__(dispatcher)

        self.calendar = calendar_handler
        self.sign_up = SignUp(dispatcher, calendar_handler)

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._timetable,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE.value)
        self.dispatcher.register_message_handler(
            self._show_timetable_future,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE_FUTURE.value)
        self.dispatcher.register_message_handler(
            self._show_timetable_history,
            lambda message: message.text == Buttons.CLIENT_TIMETABLE_HISTORY.value)
        self.sign_up.init()

    def get_user_type(self):
        return enums.UserType.CLIENT

    def get_main_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE.value, Buttons.CLIENT_ADD_TIMETABLE_ENTRY.value

    def get_timetable_buttons(self) -> Tuple[str, ...]:
        return Buttons.CLIENT_TIMETABLE_FUTURE.value, Buttons.CLIENT_TIMETABLE_HISTORY.value

    async def _show_timetable_future(self, message: types.Message):
        entries = self._get_timetable(message.from_user.id, True)
        if not entries:
            await message.answer('У вас пока нет будущих записей')
            return

        entries.sort(key=lambda entry: entry.start_dt)
        button_names = tuple(self._get_button_name(entry) for entry in entries)
        await message.answer('Ваши ближайшие записи:', reply_markup=keyboard.create_reply_keyboard_markup(button_names))

    async def _show_timetable_history(self, message: types.Message):
        entries = self._get_timetable(message.from_user.id, False)
        if not entries:
            await message.answer('У вас пока нет прошедших записей')
            return

        entries.sort(key=lambda entry: entry.start_dt)
        button_names_gen = (self._get_button_name(entry) for entry in entries)

        markup = InlineKeyboardMarkup()
        for button_name in button_names_gen:
            markup.add(InlineKeyboardButton(button_name, callback_data='button'))

        await message.answer('Выбрите элемент для открытия более подробной информации:', reply_markup=markup)

    def _get_timetable(self, user_id: int, is_future: bool) -> List[containers.TimetableEntry]:
        # try:
        #     entries = self.timetable_provider.get_by_user_id(user_id)
        # except exceptions.TimetableEntryIsNotFound:
        #     return []
        #
        # now = datetime.today()
        # if is_future:
        #     return self._get_future_entries(entries, now)
        #
        # return self._get_past_entries(entries, now)
        pass

    @staticmethod
    def _get_future_entries(entries, now) -> List[containers.TimetableEntry]:
        return [entry for entry in entries if entry.start_dt >= now]

    @staticmethod
    def _get_past_entries(entries, now) -> List[containers.TimetableEntry]:
        return [entry for entry in entries if entry.start_dt < now]

    @staticmethod
    def _get_button_name(entry: containers.TimetableEntry):
        return f'{entry.start_dt} - {entry.service_name}'

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from scheduler_core import enums, containers, configs
from wrappers import LoggerWrap

import exceptions
from handlers import states
from handlers.abstract_handler import AbstractHandler
from handlers.calendar import Calendar
from handlers.client.client import Client
from handlers.worker.worker import Worker
from managers.service import ServiceManager
from managers.timetable import TimetableManager
from managers.user import UserManager
from view import static, keyboard
from view.buttons import Buttons


async def cancel(message: types.Message, state: FSMContext) -> None:
    await reset(message, static.START, state)


async def reset(message: types.Message, message_text: str, state: FSMContext) -> None:
    await state.finish()
    await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')


async def set_user(user: containers.User, state: FSMContext) -> None:
    await state.update_data(data={'user': user})


async def get_user(state: FSMContext) -> containers.User:
    data = await state.get_data()
    return data['user']


class Handler(AbstractHandler):
    _user_manager: UserManager
    _service_manager: ServiceManager
    _calendar: Calendar
    _worker: Worker
    _client: Client

    def __init__(self, dispatcher: Dispatcher, api_connection: configs.ConnectionConfig):
        super().__init__(dispatcher)

        self._user_manager = UserManager(api_connection)
        self._service_manager = ServiceManager(api_connection)
        self._timetable_manager = TimetableManager(api_connection)

        self._calendar = Calendar(dispatcher)
        self._worker = Worker(dispatcher, self._service_manager, self._timetable_manager)
        self._client = Client(dispatcher, self._service_manager, self._timetable_manager, self._user_manager,
                              self._calendar)

    def init(self) -> None:
        self._dispatcher.register_message_handler(self._start, commands=['start'], state='*')
        self._dispatcher.register_message_handler(
            cancel,
            lambda message: message.text == Buttons.COMPLETE.value,
            state='*'
        )
        self._dispatcher.register_callback_query_handler(
            self._cancel_from_inline_keyboard,
            lambda callback_query: callback_query.data and callback_query.data == Buttons.COMPLETE.value,
            state='*'
        )
        self._dispatcher.register_message_handler(
            self._show_main_page,
            lambda message: message.text == Buttons.BACK_TO_HOME.value,
            state='*'
        )
        self._dispatcher.register_callback_query_handler(
            self._show_main_page_from_inline_keyboard,
            lambda callback_query: callback_query.data and callback_query.data == Buttons.BACK_TO_HOME.value,
            state='*'
        )

        self._calendar.init()
        self._worker.init()
        self._client.init()

    async def _start(self, message: types.Message, state: FSMContext):
        await reset(message, static.BOT_DESCRIPTION, state)

        try:
            user = await self._user_manager.get_user(message.from_user)
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(str(e))
            await message.answer(static.INTERNAL_ERROR)
            await cancel(message, state)
            return

        LoggerWrap().get_logger().info(user)
        await state.reset_data()
        await set_user(user, state)
        await self._show_main_page(message, state)

    async def _show_main_page(self, message: types.Message, state: FSMContext):
        user = await get_user(state)
        await state.reset_data()
        await set_user(user, state)

        if user.type == enums.UserType.WORKER:
            buttons = self._worker.get_main_buttons()
            await states.BotStates.worker_page.main_page.set()
        else:
            buttons = self._client.get_main_buttons()
            await states.BotStates.client_page.main_page.set()

        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup(buttons, with_home=False)
        )

    async def _cancel_from_inline_keyboard(self, query: types.CallbackQuery):
        await cancel(query.message, self._dispatcher.current_state())

    async def _show_main_page_from_inline_keyboard(self, query: types.CallbackQuery):
        await self._show_main_page(query.message, self._dispatcher.current_state())

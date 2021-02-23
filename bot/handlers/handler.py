from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from scheduler_core import enums, containers, configs
from wrappers import LoggerWrap

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


async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(static.START, reply_markup=types.ReplyKeyboardRemove())


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
        self._worker = Worker(dispatcher)
        self._client = Client(dispatcher, self._service_manager, self._timetable_manager, self._user_manager,
                              self._calendar)

    def init(self) -> None:
        self.dispatcher.register_message_handler(self._start, commands=['start'])
        self.dispatcher.register_message_handler(
            cancel,
            lambda message: message.text == Buttons.CANCEL.value,
            state='*'
        )

        self._calendar.init()
        self._worker.init()
        self._client.init()

    async def _start(self, message: types.Message, state: FSMContext):
        user = await self._user_manager.get_user(message.from_user)
        LoggerWrap().get_logger().info(user)
        await state.update_data(data={'user': user})
        await self._show_main_page(message, user)

    async def _show_main_page(self, message: types.Message, user: containers.User):
        if user.type == enums.UserType.WORKER:
            buttons = self._worker.get_main_buttons()
            await states.BotStates.worker_page.main_page.set()
        else:
            buttons = self._client.get_main_buttons()
            await states.BotStates.client_page.main_page.set()

        await message.answer(static.SELECT_ITEM, reply_markup=keyboard.create_reply_keyboard_markup(buttons))

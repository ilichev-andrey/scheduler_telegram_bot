from aiogram import Dispatcher, types
from scheduler_core import enums, containers, configs
from wrappers import LoggerWrap

from handlers.abstract_handler import AbstractHandler
from handlers.calendar import Calendar
from handlers.client.client import Client
from handlers.worker.worker import Worker
from managers.user import UserManager
from view import static, keyboard


class Handler(AbstractHandler):
    _user_manager: UserManager
    _calendar: Calendar
    _worker: Worker
    _client: Client

    def __init__(self, dispatcher: Dispatcher, api_connection: configs.ConnectionConfig):
        super().__init__(dispatcher)

        self._user_manager = UserManager(api_connection)
        self._calendar = Calendar(dispatcher)
        self._worker = Worker(dispatcher)
        self._client = Client(dispatcher, self._calendar)

    def init(self) -> None:
        self.dispatcher.register_message_handler(self._start, commands=['start'])
        # self.calendar.init()
        # self.worker.init()
        # self.client.init()

    async def _start(self, message: types.Message):
        user = await self._user_manager.get_user(message.from_user)
        LoggerWrap().get_logger().info(user)
        await self.show_main_page(message, user)

    async def show_main_page(self, message: types.Message, user: containers.User):
        if user.type == enums.UserType.WORKER:
            reply_markup = keyboard.create_reply_keyboard_markup(self._worker.get_main_buttons())
        else:
            reply_markup = keyboard.create_reply_keyboard_markup(self._client.get_main_buttons())

        await message.answer(static.SELECT_ITEM, reply_markup=reply_markup)

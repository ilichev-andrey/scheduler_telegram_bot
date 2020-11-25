from aiogram import Dispatcher, types

from bot.enums import UserType
from database.exceptions import UserIsNotFound
from bot.handlers import AbstractHandler, Calendar
from bot.handlers.client import Client
from bot.handlers.worker import Worker
from bot.view import static, keyboard
from database import DB, provider
from wrappers import LoggerWrap


class Handler(AbstractHandler):
    def __init__(self, dispatcher: Dispatcher, db: DB):
        super().__init__(dispatcher)

        self.user_provider = provider.User(db)
        self.service_provider = provider.Service(db)
        self.timetable_provider = provider.Timetable(db)

        self.calendar = Calendar(dispatcher)
        self.worker = Worker(dispatcher, self.service_provider)
        self.client = Client(dispatcher, db, self.service_provider, self.calendar)

    def init(self) -> None:
        self.dispatcher.register_message_handler(self.__start, commands=['start'])
        self.calendar.init()
        self.worker.init()
        self.client.init()

    async def __start(self, message: types.Message):
        try:
            user = self.user_provider.get_by_id(message.from_user.id)
        except UserIsNotFound as e:
            LoggerWrap().get_logger().exception(e)
            user = self.user_provider.add(message.from_user)

        LoggerWrap().get_logger().info(user)
        if user.type == UserType.WORKER:
            reply_markup = keyboard.create_reply_keyboard_markup(self.worker.get_main_buttons())
        else:
            reply_markup = keyboard.create_reply_keyboard_markup(self.client.get_main_buttons())

        await message.answer(static.SELECT_ITEM, reply_markup=reply_markup)

from aiogram import Dispatcher, types

import bot.view.keyboard as keyboard
from bot.enums import UserType
from database.exceptions import UserIsNotFound
from bot.handlers import calendar
from bot.handlers.client import client
from bot.handlers.worker import worker
from bot.view import static
from database.db import DB
from wrappers.logger import LoggerWrap


class Handler(object):
    def __init__(self, dispatcher: Dispatcher, db: DB):
        self.dispatcher = dispatcher
        self.db = db

        self.calendar = calendar.Calendar(self.dispatcher)
        self.worker = worker.Worker(self.dispatcher)
        self.client = client.Client(self.dispatcher, self.db, self.calendar)

    def init(self) -> None:
        self.dispatcher.register_message_handler(self.__start, commands=['start'])
        self.calendar.init()
        self.worker.init()
        self.client.init()

    async def __start(self, message: types.Message):
        try:
            user = self.db.get_user_by_id(message.from_user.id)
        except UserIsNotFound as e:
            LoggerWrap().get_logger().exception(e)
            user = self.db.add_user(message.from_user)

        LoggerWrap().get_logger().info(user)
        if user.type == UserType.WORKER:
            reply_markup = keyboard.create_reply_keyboard_markup(self.worker.get_main_buttons())
        else:
            reply_markup = keyboard.create_reply_keyboard_markup(self.client.get_main_buttons())

        await message.answer(static.SELECT_ITEM, reply_markup=reply_markup)

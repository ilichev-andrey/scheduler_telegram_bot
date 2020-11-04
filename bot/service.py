from typing import AnyStr, Dict

from aiogram import Bot, Dispatcher, executor, types

import bot.view.keyboard as keyboard
from bot.enums import UserType
from bot.exceptions import UserIsNotFound
from bot.handlers import client, worker
from database.db import DB


class Service(object):
    def __init__(self, api_token: AnyStr, config: Dict):
        self.db = DB(config['database'])
        self.dispatcher = Dispatcher(Bot(token=api_token))
        self.worker = worker.Worker(self.dispatcher)
        self.client = client.Client(self.dispatcher)

    def init_handlers(self):
        self.dispatcher.register_message_handler(self.__cmd_start, commands=['start'])
        self.client.init()
        self.worker.init()

    def run(self):
        executor.start_polling(self.dispatcher, skip_updates=False)

    async def __cmd_start(self, message: types.Message):
        try:
            user = self.db.get_user_by_id(message.from_user.id)
        except UserIsNotFound:
            user = self.db.add_user()

        if user.type == UserType.WORKER:
            reply_markup = keyboard.create_reply_keyboard_markup(self.worker.get_main_buttons())
        else:
            reply_markup = keyboard.create_reply_keyboard_markup(self.client.get_main_buttons())

        await message.answer('Выберите пункт:', reply_markup=reply_markup)

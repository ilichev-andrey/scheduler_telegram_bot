from typing import AnyStr, Dict

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor

from bot.handlers import handler
from bot.middlewares import AccessMiddleware
from database.db import DB


class Service(object):
    def __init__(self, api_token: AnyStr, config: Dict, database_password: str):
        self.dispatcher = Dispatcher(Bot(token=api_token), storage=MemoryStorage())
        self.dispatcher.middleware.setup(AccessMiddleware())
        self.handler = handler.Handler(self.dispatcher, DB(config['database'], database_password))

    def init(self):
        self.handler.init()

    def run(self):
        executor.start_polling(self.dispatcher, skip_updates=False)

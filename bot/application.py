from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor

import configs
from handlers import handler
from middlewares import AccessMiddleware


class Application(object):
    _config: configs.Config
    _dispatcher: Dispatcher
    _handler: handler.Handler

    def __init__(self, config: configs.Config, api_token: str):
        self._config = config
        self._dispatcher = Dispatcher(Bot(token=api_token), storage=MemoryStorage())
        self._dispatcher.middleware.setup(AccessMiddleware())
        self._handler = handler.Handler(self._dispatcher, config.api_connection)

    def init(self):
        self._handler.init()

    def run(self):
        executor.start_polling(self._dispatcher, skip_updates=False)

from abc import ABC, abstractmethod

from aiogram import Dispatcher


class AbstractHandler(ABC):
    _dispatcher: Dispatcher

    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher = dispatcher

    @abstractmethod
    def init(self) -> None:
        pass

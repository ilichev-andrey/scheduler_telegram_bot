from abc import ABC, abstractmethod

from aiogram import Dispatcher


class IHandler(ABC):
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher

    @abstractmethod
    def init(self) -> None:
        pass

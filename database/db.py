from typing import Dict

from bot.enums import UserType
from database import containers


class DB(object):
    def __init__(self, config: Dict):
        self.config = config

    def add_user(self) -> containers.User:
        pass

    @staticmethod
    def get_user_by_id(user_id: int) -> containers.User:
        return containers.User(user_id, UserType.WORKER)

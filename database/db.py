from typing import Dict

import psycopg2
from psycopg2 import extras, extensions
from aiogram.types import User

from bot.enums import UserType
from bot.exceptions import UserIsNotFound
from database import containers
from wrappers.logger import LoggerWrap


class DB(object):
    con: extensions.connection

    def __init__(self, config: Dict, password: str):
        self.con = psycopg2.connect(password=password, **config)

    def __del__(self):
        self.con.close()

    def add_user(self, user: User) -> containers.User:
        LoggerWrap().get_logger().info(f'Добавление пользователя: {user}')
        user = containers.User(user.id, UserType.CLIENT, user.first_name, user.last_name, user.username)

        cursor = self.con.cursor()
        cursor.execute('''
            INSERT INTO users (id, type, first_name, last_name, username)
            VALUES(%(id)s, %(type)s, %(first_name)s, %(last_name)s, %(username)s)
        ''', user.asdict())

        self.con.commit()
        cursor.close()

        return user

    def get_user_by_id(self, user_id: int) -> containers.User:
        cursor = self.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            SELECT id, type, first_name, last_name, username
            FROM users
            WHERE id=%s
        ''', (user_id,))

        user = cursor.fetchone()
        cursor.close()

        if not user:
            raise UserIsNotFound(f'Не найден пользователь с id={user_id}')

        LoggerWrap().get_logger().info(f'Получена запись из таблицы пользователей: {user}')
        return containers.make_user(**user)

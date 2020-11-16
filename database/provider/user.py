from aiogram import types
from psycopg2 import extras

from bot.enums import UserType
from database import DB, containers, exceptions
from wrappers import LoggerWrap


class User(object):
    def __init__(self, db: DB):
        self.db = db

    def add(self, user: types.User) -> containers.User:
        LoggerWrap().get_logger().info(f'Добавление пользователя: {user}')
        user = containers.User(user.id, UserType.CLIENT, user.first_name, user.last_name, user.username)

        cursor = self.db.con.cursor()
        cursor.execute('''
            INSERT INTO users (id, type, first_name, last_name, username)
            VALUES(%(id)s, %(type)s, %(first_name)s, %(last_name)s, %(username)s)
        ''', user.asdict())

        self.db.con.commit()
        cursor.close()
        return user

    def get_by_id(self, user_id: int) -> containers.User:
        cursor = self.db.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            SELECT id, type, first_name, last_name, username
            FROM users
            WHERE id=%s
        ''', (user_id,))

        user = cursor.fetchone()
        cursor.close()

        if not user:
            raise exceptions.UserIsNotFound(f'Не найден пользователь с id={user_id}')

        LoggerWrap().get_logger().info(f'Получена запись из таблицы пользователей: {user}')
        return containers.make_user(**user)

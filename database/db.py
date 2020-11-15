from datetime import date
from typing import Dict, List

import psycopg2
from aiogram.types import User
from psycopg2 import extras, extensions

from bot.enums import UserType
from database import containers, exceptions
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
            raise exceptions.UserIsNotFound(f'Не найден пользователь с id={user_id}')

        LoggerWrap().get_logger().info(f'Получена запись из таблицы пользователей: {user}')
        return containers.make_user(**user)

    def get_services(self) -> List[containers.Service]:
        cursor = self.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            SELECT id, name, time_interval
            FROM services
        ''')

        services = cursor.fetchall()
        cursor.close()

        if not services:
            raise exceptions.ServiceIsNotFound(f'Не найдена ни одна услуга')

        return [containers.make_service(**service) for service in services]

    def get_timetable_by_day(self, day: date) -> List[containers.TimetableEntry]:
        cursor = self.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            SELECT 
                id,
                worker_id,
                client_id,
                service_id,
                extract(epoch from create_dt) as create_dt,
                extract(epoch from start_dt) as start_dt
            FROM public.timetable
            where 
                start_dt >= %(day)s::date
                and start_dt < %(day)s::date+1
                and client_id isnull 
        ''', {'day': day})

        entries = cursor.fetchall()
        cursor.close()

        LoggerWrap().get_logger().info(f'Получены записи из таблицы расписания: {entries}')
        if not entries:
            raise exceptions.TimetableEntryIsNotFound(f'Не найдена ни одна запись в распивании')

        return [containers.make_timetable_entry(**entry) for entry in entries]

    def update_timetable_entry(self, timetable_id: int, service_id: int, user_id: int):
        cursor = self.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            UPDATE timetable 
            SET client_id=%s, service_id=%s
            WHERE id=%s
        ''', (user_id, service_id, timetable_id))

        self.con.commit()
        cursor.close()

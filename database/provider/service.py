from typing import List

from psycopg2 import Error, errorcodes
from psycopg2 import extras

from database import DB, containers, exceptions


class Service(object):
    def __init__(self, db: DB):
        self.db = db

    def get(self) -> List[containers.Service]:
        cursor = self.db.con.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute('''
            SELECT id, name, time_interval
            FROM services
        ''')

        services = cursor.fetchall()
        cursor.close()

        if not services:
            raise exceptions.ServiceIsNotFound(f'Не найдена ни одна услуга')

        return [containers.make_service(**service) for service in services]

    def add(self, name: str):
        cursor = self.db.con.cursor()
        try:
            cursor.execute('''
                INSERT INTO services (name)
                VALUES (%s)
            ''', (name,))
            self.db.con.commit()
        except Error as e:
            if e.pgcode == errorcodes.UNIQUE_VIOLATION:
                raise exceptions.ServiceAlreadyExists(f'{name} уже существует')
            raise exceptions.BaseBotException(str(e))
        finally:
            cursor.close()

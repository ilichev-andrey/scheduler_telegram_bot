from typing import List

from psycopg2 import extras

from database import containers, exceptions
from database import DB


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

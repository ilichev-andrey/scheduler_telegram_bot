from typing import Dict

import psycopg2
from psycopg2 import extensions


class DB(object):
    con: extensions.connection

    def __init__(self, config: Dict, password: str):
        self.con = psycopg2.connect(password=password, **config)

    def __del__(self):
        self.con.close()






from database import DB


class Timetable(object):
    def __init__(self, db: DB):
        self.db = db

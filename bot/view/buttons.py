from enum import Enum, unique


class Buttons(Enum):
    WORKER_TIMETABLE = 'Показать расписание'
    WORKER_TIMETABLE_ENTRY = 'Записать'
    WORKER_TIMETABLE_TODAY = 'На сегодня'
    WORKER_TIMETABLE_WEEK = 'На неделю'

    CLIENT_TIMETABLE = 'Показать  мои записи'
    CLIENT_TIMETABLE_ENTRY = 'Записаться'
    CLIENT_TIMETABLE_FUTURE = 'Будущие записи'
    CLIENT_TIMETABLE_HISTORY = 'История записей'


# Текст кнопок должен быть уникальный, т.к. на них подвешиваются разные события
unique(Buttons)

from enum import Enum, unique


class Buttons(Enum):
    WORKER_TIMETABLE = 'Показать расписание'
    WORKER_ADD_TIMETABLE_ENTRY = 'Записать'
    WORKER_TIMETABLE_TODAY = 'На сегодня'
    WORKER_TIMETABLE_WEEK = 'На неделю'
    WORKER_SERVICES = 'Услуги'
    WORKER_SHOW_SERVICES = 'Показать все'
    WORKER_ADD_SERVICES = 'Добавить'
    WORKER_DELETE_SERVICES = 'Удалить'
    WORKER_EDIT_SERVICES = 'Редактировать'

    CLIENT_TIMETABLE = 'Показать мои записи'
    CLIENT_ADD_TIMETABLE_ENTRY = 'Записаться'
    CLIENT_TIMETABLE_FUTURE = 'Будущие записи'
    CLIENT_TIMETABLE_HISTORY = 'История записей'

    PREV_STEP = 'Назад'
    NEXT_STEP = 'Далее'
    RESUME = 'Продолжить'
    CANCEL = 'Отмена'


# Текст кнопок должен быть уникальный, т.к. на них подвешиваются разные события
unique(Buttons)

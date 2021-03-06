from datetime import date, datetime

from aiogram.utils.markdown import link
from scheduler_core import enums, containers

from bot import converter

instagram_link = link('dinail58', 'https://instagram.com/dinail58?igshid=6aw9ki1im567')
support_link = link('support', 'https://t.me/@ilichev_andrey')

CONTACT_SUPPORT = f'Свяжитесь с нами в {support_link}'
BOT_DESCRIPTION = f'Приветствую! Я бот, созданный для {instagram_link}.\n{CONTACT_SUPPORT} при возникновении проблем.'

INTERNAL_ERROR = f'Ой, что-то пошло не так.\nПовторите попытку позже или {CONTACT_SUPPORT.lower()}.'
EMPTY_TEXT = '⁣'
DASH_TEXT = '———————————'

SELECT = 'Выберите'
SELECT_ITEM = f'{SELECT} пункт'
SELECT_DATE = f'{SELECT} дату'
SELECT_TIME = f'{SELECT} время'

SELECT_START_PERIOD = f'{SELECT} начальную дату'
SELECT_END_PERIOD = f'{SELECT} конечную дату'

SET_PHONE_NUMBER = 'Ведите номер телефона клиента'
SET_FIO = 'Ведите ФИО'

SELECTED = 'Вы выбрали'
SELECTED_SERVICE = f'{SELECTED} услугу:'
# SELECTED_DATE = f'{SELECTED} дату:'
SELECTED_TIME = f'{SELECTED} время:'

INPUT = 'Ведите'
INPUT_NAME = f'{INPUT} название'
INPUT_EXECUTION_TIME = f'{INPUT} продолжительность выполнения услуги (кол-во минут)'

WRONG_INPUT = 'Введенные данные некорректные.'

SERVICE_EXISTS = 'Услуга уже существует'
NO_SERVICES = 'Услуги не добавлены'
SERVICES = 'Услуги:'

START = 'Нажмите /start, чтобы начать'
BUSY = 'Нет свободных мест'

SEND_PHONE_NUMBER = 'Отправить номер телефона'
SEND_LOCATION = 'Отправить геолокацию'


_DETAILED_INFORMATION = 'Можно посмотреть подробную информацию, нажав на кнопку ниже:'
_CHANGE_INFORMATION = 'Можно изменить запись, нажав на кнопку ниже:'

ADD_BUTTON = 'Добавить'


def get_successful_registration_text(service_name: str, dt: datetime, client: str = None) -> str:
    if client is None:
        text = 'Вы записаны'
    else:
        text = f'Клиент: {client} записан'

    return f'{text} на услугу: {service_name} в {converter.to_human_datetime(dt)}'


def get_successful_add_service(service_name: str, execution_time_minutes: int) -> str:
    return f'Добавлена услуга: {service_name} продолжительностью {execution_time_minutes} минут'


def get_selected_date_text(selected_date: date) -> str:
    return f'Вы выбрали дату: {converter.to_human_date(selected_date)}. Нажмите для продолжения.'


def get_worker_timetable_title(time_type: enums.TimeType, time_limit: enums.TimeLimit, is_found: bool = True) -> str:
    title = ''
    if time_limit == enums.TimeLimit.DAY:
        title = 'текущий день:'
    else:
        if time_type == enums.TimeType.PAST:
            title = 'прошедш'
        if time_type == enums.TimeType.FUTURE:
            title = 'будущ'

        if time_limit == enums.TimeLimit.WEEK:
            title = f'{title}ую неделю:'
        if time_limit == enums.TimeLimit.MONTH:
            title = f'{title}ий месяц:'

    if is_found:
        return f'Записи на {title}\n{_DETAILED_INFORMATION}'
    else:
        return f'Нет записей на {title}'


def get_client_timetable_title(time_type: enums.TimeType, is_found: bool = True) -> str:
    if time_type == enums.TimeType.PAST:
        if is_found:
            return f'Ваши прошедшие записи:\n{_DETAILED_INFORMATION}'
        else:
            return 'У вас ранее не было записей'
    else:
        if is_found:
            return f'Ваши ближайшие записи:\n{_CHANGE_INFORMATION}'
        else:
            return 'У вас пока нет будущих записей'


def get_detail_client_timetable(entry: containers.TimetableEntry, time_type: enums.TimeType) -> str:
    to_be = ''
    if time_type == enums.TimeType.PAST:
        to_be = 'были '

    return 'Информация о записи:\n' \
           f'Вы {to_be}записаны на услугу: {entry.service_name}\n' \
           f'Дата: {converter.to_human_datetime(entry.start_dt)}\n' \
           f'Работник: {entry.worker_id}'


def get_detail_release_client_timetable(entry: containers.TimetableEntry) -> str:
    return f'Запись ОТМЕНЕНА:\nУслуга: {entry.service_name}\n' \
           f'Дата: {converter.to_human_datetime(entry.start_dt)}\n' \
           f'Работник: {entry.worker_id}'

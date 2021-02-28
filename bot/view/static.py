from datetime import date, datetime

from aiogram.utils.markdown import link

import converter

instagram_link = link('dinail58', 'https://instagram.com/dinail58?igshid=6aw9ki1im567')

BOT_DESCRIPTION = f'Приветствую! Я бот, созданный для {instagram_link}'

INTERNAL_ERROR = 'Ой, что-то пошло не так. Повторите попытку позже.'

SELECT = 'Выберите'
SELECT_ITEM = f'{SELECT} пункт'
SELECT_DATE = f'{SELECT} дату'
SELECT_TIME = f'{SELECT} время'

SELECTED = 'Вы выбрали'
SELECTED_SERVICE = f'{SELECTED} услугу:'
# SELECTED_DATE = f'{SELECTED} дату:'
SELECTED_TIME = f'{SELECTED} время:'

INPUT = 'Ведите'
INPUT_NAME = f'{INPUT} название'

WRONG_INPUT = 'Неккоректные вводимые данные.'

SERVICE_ADDED = 'Добавлена услуга:'
SERVICE_EXISTS = 'Услуга уже существует'

START = 'Нажмите /start, чтобы начать'
BUSY = 'Нет свободных мест'

SEND_PHONE_NUMBER = 'Отправить номер телефона'
SEND_LOCATION = 'Отправить геолокацию'


def get_successful_registration_text(service_name: str, dt: datetime) -> str:
    return f'Вы записаны на услугу {service_name} в {converter.to_human_datetime(dt)}'


def get_selected_date_text(selected_date: date) -> str:
    return f'Вы выбрали дату: {converter.to_human_date(selected_date)}. Нажмите для продолжения.'

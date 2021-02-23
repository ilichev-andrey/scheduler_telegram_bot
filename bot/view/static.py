from datetime import datetime

INTERNAL_ERROR = 'Ой, что-то пошло не так. Повторите попытку позже.'

SELECT = 'Выберите'
SELECT_ITEM = f'{SELECT} пункт:'
SELECT_DATE = f'{SELECT} дату:'
SELECT_TIME = f'{SELECT} время:'

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


def get_successful_registration_text(service_name: str, dt: datetime) -> str:
    return f'Вы записаны на услугу {service_name} в {dt}'


def get_selected_date_text(selected_date: str) -> str:
    return f'Вы выбрали дату: {selected_date}. Нажмите для продолжения.'

from aiogram.dispatcher.filters.state import State, StatesGroup


class ClientRequestStates(StatesGroup):
    waiting_service = State()
    waiting_date = State()
    waiting_time = State()
    cancel = State()

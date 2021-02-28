from aiogram.dispatcher.filters.state import StatesGroup, State


class SignUpStates(StatesGroup):
    select_date = State()
    select_time = State()
    set_phone_number = State()
    add_timetable_entry = State()


class ClientStates(StatesGroup):
    main_page = State()
    timetable_page = State()
    visit_history = State()
    future_visits = State()
    sign_up = SignUpStates


class WorkerStates(StatesGroup):
    main_page = State()


class BotStates(StatesGroup):
    client_page = ClientStates
    worker_page = WorkerStates

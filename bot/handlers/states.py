from aiogram.dispatcher.filters.state import StatesGroup, State


class ClientSignUpStates(StatesGroup):
    select_date = State()
    select_time = State()
    set_phone_number = State()
    add_timetable_entry = State()


class ClientStates(StatesGroup):
    main_page = State()
    timetable_page = State()
    visit_history = State()
    future_visits = State()
    sign_up = ClientSignUpStates


class ServiceStates(StatesGroup):
    main_page = State()
    show = State()
    add = State()
    delete = State()
    input_name = State()
    input_execution_time = State()


class WorkerSignUpStates(StatesGroup):
    select_date = State()
    select_time = State()
    set_phone_number = State()
    set_fio = State()
    add_timetable_entry = State()


class WorkerStates(StatesGroup):
    main_page = State()
    timetable_page = State()
    service = ServiceStates
    sign_up = WorkerSignUpStates


class BotStates(StatesGroup):
    client_page = ClientStates
    worker_page = WorkerStates

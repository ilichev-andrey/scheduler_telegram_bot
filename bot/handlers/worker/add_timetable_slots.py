import math
from datetime import date, datetime, time, timedelta
from typing import List, Dict

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from scheduler_core import enums, containers

from bot import converter, exceptions
from bot.handlers import states, handler
from bot.handlers.abstract_handler import AbstractHandler
from bot.handlers.calendar import Calendar
from bot.managers.timetable import TimetableManager
from bot.view import static, keyboard
from bot.view.buttons import Buttons


def _generate_times(start_tm: time, end_tm: time, step=30) -> Dict[str, time]:
    def time_to_minutes(tm: time) -> int:
        return int(timedelta(hours=tm.hour, minutes=tm.minute, seconds=tm.second).total_seconds() / 60)

    _start_dt = (datetime.combine(date.today(), time()) +
                 timedelta(minutes=math.ceil(time_to_minutes(start_tm) / step) * step))
    time_diff = time_to_minutes(end_tm) - time_to_minutes(_start_dt.time())

    times = {}
    for i in range(0, time_diff, step):
        _time = (_start_dt + timedelta(minutes=i)).time()
        times[converter.to_human_time(_time)] = _time

    return times


class AddTimetableSlots(AbstractHandler):
    _BUTTON_PREFIX = 'add_slots_btn_'
    _ADD_SLOTS_BUTTON = f'complete_{_BUTTON_PREFIX}'

    _timetable_manager: TimetableManager
    _calendar: Calendar

    def __init__(self, dispatcher: Dispatcher, timetable_manager: TimetableManager, calendar_handler: Calendar):
        super().__init__(dispatcher)
        self._timetable_manager = timetable_manager
        self._calendar = calendar_handler

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._select_type,
            lambda message: message.text == Buttons.WORKER_ADD_TIMETABLE_SLOTS.value,
            state=states.WorkerStates.main_page
        )
        self._dispatcher.register_message_handler(
            self._select_start_date,
            state=states.WorkerAddTimetableSlotsStates.select_start_date
        )
        self._dispatcher.register_message_handler(
            self._select_end_date,
            state=states.WorkerAddTimetableSlotsStates.select_end_date
        )
        self._dispatcher.register_message_handler(
            self._select_times,
            state=states.WorkerAddTimetableSlotsStates.select_times
        )
        self._dispatcher.register_callback_query_handler(
            self._select_times_callback_query,
            lambda callback_query: callback_query.data and callback_query.data.startswith(self._BUTTON_PREFIX),
            state=states.WorkerAddTimetableSlotsStates.select_times
        )
        self._dispatcher.register_callback_query_handler(
            self._add_slots,
            lambda callback_query: callback_query.data and callback_query.data == self._ADD_SLOTS_BUTTON,
            state=states.WorkerAddTimetableSlotsStates.select_times
        )

    @staticmethod
    async def _select_type(message: types.Message):
        await states.WorkerAddTimetableSlotsStates.select_start_date.set()
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup((Buttons.WORKER_TIMETABLE_PERIOD.value,))
        )

    async def _select_start_date(self, message: types.Message, state: FSMContext):
        try:
            entries = await self._timetable_manager.get_worker_timetable(
                worker_id=(await handler.get_user(state)).id,
                time_type=enums.TimeType.FUTURE,
                time_limit=enums.TimeLimit.NO_LIMIT
            )
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        exclude_dates = {entry.start_dt.date() for entry in entries}
        await state.update_data(data={'exclude_dates': exclude_dates})

        await message.answer(static.SELECT_START_PERIOD)
        await self._calendar.open(
            message,
            on_selected_date=lambda chosen_date: self._on_selected_date(chosen_date, message, state),
            exclude_dates=exclude_dates
        )

    async def _select_end_date(self, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        exclude_dates = user_data['exclude_dates']

        await message.answer(static.SELECT_END_PERIOD)
        await self._calendar.open(
            message,
            on_selected_date=lambda chosen_date: self._on_selected_date(chosen_date, message, state),
            exclude_dates=exclude_dates
        )

    @staticmethod
    async def _on_selected_date(chosen_date: date, message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        chosen_dates = user_data.get('chosen_dates', [])
        chosen_dates.append(datetime.combine(chosen_date, time()))
        await state.update_data(data={'chosen_dates': chosen_dates})

        if len(chosen_dates) == 1:
            await states.WorkerAddTimetableSlotsStates.select_end_date.set()
            await message.answer(
                static.SELECT_ITEM,
                reply_markup=keyboard.create_reply_keyboard_markup((static.SELECT_END_PERIOD,))
            )
        else:
            await states.WorkerAddTimetableSlotsStates.select_times.set()
            await message.answer(
                static.SELECT_ITEM,
                reply_markup=keyboard.create_reply_keyboard_markup((static.SELECT_TIME,))
            )

    async def _select_times(self, message: types.Message, state: FSMContext):
        times = _generate_times(time(8), time(22))
        await state.update_data(data={'times': times})
        await message.answer(static.SELECT_TIME, reply_markup=self._create_markup_for_select_times(times, []))

    async def _select_times_callback_query(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()

        user_data = await state.get_data()
        chosen_times = user_data.get('chosen_times', [])
        chosen_times.append(query.data.removeprefix(self._BUTTON_PREFIX))
        await state.update_data(data={'chosen_times': chosen_times})

        await message.edit_reply_markup(reply_markup=self._create_markup_for_select_times(
            times=user_data['times'],
            chosen_times=chosen_times
        ))

    def _create_markup_for_select_times(self, times: Dict[str, time], chosen_times: List[str]) -> InlineKeyboardMarkup:
        chosen_times.sort()
        chosen_times_set = set(chosen_times)
        markup = InlineKeyboardMarkup()
        for _time in times:
            if _time in chosen_times_set:
                _time = ' '
            markup.add(InlineKeyboardButton(text=_time, callback_data=f'{self._BUTTON_PREFIX}{_time}'))

        markup.add(InlineKeyboardButton(text=static.DASH_TEXT, callback_data='None'))
        markup.add(InlineKeyboardButton(text=f'{static.SELECTED}:', callback_data='None'))
        for chosen_time in chosen_times:
            markup.add(InlineKeyboardButton(text=chosen_time, callback_data='None'))

        markup.add(InlineKeyboardButton(text=static.DASH_TEXT, callback_data='None'))
        markup.add(InlineKeyboardButton(text=static.ADD_BUTTON, callback_data=self._ADD_SLOTS_BUTTON))
        return markup

    async def _add_slots(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()

        user_data = await state.get_data()
        chosen_dates = user_data['chosen_dates']
        try:
            dates = await self._timetable_manager.add_slots(
                date_ranges=containers.DateRanges(*chosen_dates),
                times=[converter.from_human_time(chosen_time) for chosen_time in user_data['chosen_times']],
                worker_id=(await handler.get_user(state)).id
            )
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        await message.delete()
        await message.answer(f'OK. data {dates}')

from datetime import date
from typing import Set

from aiogram import types, Dispatcher
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP
from telegram_bot_calendar.static import Locales

from bot.view import static
from handlers.abstract_handler import AbstractHandler


class Calendar(AbstractHandler):
    _on_selected_date: callable
    _calendar: WMonthTelegramCalendar

    def __init__(self, dispatcher: Dispatcher, months_future_count: int = 2):
        super().__init__(dispatcher)
        self._on_selected_date = None
        today = date.today()
        self._calendar = WMonthTelegramCalendar(
            locale=Locales.RUSSIAN,
            min_date=today,
            max_date=today + relativedelta(months=months_future_count))

    def init(self) -> None:
        self._dispatcher.register_callback_query_handler(self._handle_callback_query, self._calendar.func(), state='*')

    async def open(self, message: types.Message, on_selected_date: callable = None, include_dates: Set[date] = None):
        self._on_selected_date = on_selected_date
        self._calendar.include_dates = include_dates

        calendar, step = self._calendar.build()
        await self._dispatcher.bot.send_message(
            chat_id=message.chat.id,
            text=f'{static.SELECT} {LSTEP[step]}',
            reply_markup=calendar
        )

    async def _handle_callback_query(self, query):
        result, key, step = self._calendar.process(query.data)

        if not result and key:
            await self._dispatcher.bot.edit_message_text(
                f'{static.SELECT} {LSTEP[step]}',
                query.message.chat.id,
                query.message.message_id,
                reply_markup=key)
        elif result:
            await self._dispatcher.bot.delete_message(query.message.chat.id, query.message.message_id)
            if self._on_selected_date is not None:
                await self._on_selected_date(result)

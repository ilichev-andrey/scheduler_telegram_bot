from datetime import date
from typing import Set

from aiogram import types, Dispatcher
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP
from telegram_bot_calendar.static import Locales

from bot.view import static
from handlers.abstract_handler import AbstractHandler


class Calendar(AbstractHandler):
    on_selected_date = None

    def __init__(self, dispatcher: Dispatcher, months_future_count=2):
        super().__init__(dispatcher)
        today = date.today()
        self.calendar = WMonthTelegramCalendar(
            locale=Locales.RUSSIAN,
            min_date=today,
            max_date=today + relativedelta(months=months_future_count))

    def init(self) -> None:
        self.dispatcher.register_callback_query_handler(self._handle_callback_query, self.calendar.func(), state='*')

    async def open(self, message: types.Message, on_selected_date: callable = None, include_dates: Set[date] = None):
        self.on_selected_date = on_selected_date
        self.calendar.include_dates = include_dates

        calendar, step = self.calendar.build()
        await self.dispatcher.bot.send_message(message.chat.id, f'{static.SELECT} {LSTEP[step]}', reply_markup=calendar)

    async def _handle_callback_query(self, query):
        result, key, step = self.calendar.process(query.data)

        if not result and key:
            await self.dispatcher.bot.edit_message_text(
                f'{static.SELECT} {LSTEP[step]}',
                query.message.chat.id,
                query.message.message_id,
                reply_markup=key)
        elif result:
            await self.dispatcher.bot.delete_message(query.message.chat.id, query.message.message_id)
            if self.on_selected_date is not None:
                await self.on_selected_date(result)

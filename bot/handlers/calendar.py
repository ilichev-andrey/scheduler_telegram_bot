from datetime import date

from aiogram import types, Dispatcher
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import WMonthTelegramCalendar, LSTEP
from telegram_bot_calendar.static import Locales

from bot.handlers.ihandler import IHandler


class Calendar(IHandler):
    def __init__(self, dispatcher: Dispatcher, months_future_count=2):
        super().__init__(dispatcher)
        today = date.today()
        self.calendar = WMonthTelegramCalendar(
            locale=Locales.RUSSIAN,
            min_date=today,
            max_date=today + relativedelta(months=months_future_count))

    def init(self) -> None:
        self.dispatcher.register_callback_query_handler(self.__handle_callback_query, self.calendar.func())

    async def open(self, message: types.Message):
        calendar, step = self.calendar.build()
        await self.dispatcher.bot.send_message(message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)

    async def __handle_callback_query(self, query):
        result, key, step = self.calendar.process(query.data)

        if not result and key:
            await self.dispatcher.bot.edit_message_text(
                f"Выберите {LSTEP[step]}",
                query.message.chat.id,
                query.message.message_id,
                reply_markup=key)
        elif result:
            await self.dispatcher.bot.edit_message_text(
                f"Вы выбрали {result}",
                query.message.chat.id,
                query.message.message_id)

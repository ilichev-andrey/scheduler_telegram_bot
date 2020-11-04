from typing import AnyStr, Dict

from aiogram import Bot, Dispatcher, executor, types


class Service(object):
    def __init__(self, api_token: AnyStr, config: Dict):
        self.dp = Dispatcher(Bot(token=api_token))

    def init_handlers(self):
        self.dp.register_message_handler(self.__cmd_start, commands=["start"])
        self.dp.register_message_handler(self.__action_cancel, lambda message: message.text == "Отмена")

    def run(self):
        executor.start_polling(self.dp, skip_updates=False)

    @staticmethod
    async def __cmd_start(message: types.Message):
        poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        poll_keyboard.add(types.KeyboardButton(text="Показать мои записи"))
        poll_keyboard.add(types.KeyboardButton(text="Записаться"))
        poll_keyboard.add(types.KeyboardButton(text="Отмена"))
        await message.answer("Выберите пункт или нажмите Отмена", reply_markup=poll_keyboard)

    @staticmethod
    async def __action_cancel(message: types.Message):
        remove_keyboard = types.ReplyKeyboardRemove()
        await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)

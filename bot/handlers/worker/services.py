from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.handlers import AbstractHandler
from bot.input_validators import ServiceInputValidator
from bot.view import Buttons, keyboard, static
from database import exceptions, provider
from wrappers import LoggerWrap


class ServiceStates(StatesGroup):
    input_name = State()
    add = State()
    cancel = State()


class Services(AbstractHandler):
    def __init__(self, dispatcher: Dispatcher, service_provider: provider.Service):
        super().__init__(dispatcher)
        self.service_provider = service_provider

    def init(self) -> None:
        self.dispatcher.register_message_handler(
            self._show_actions,
            lambda message: message.text == Buttons.WORKER_SERVICES.value)
        self.dispatcher.register_message_handler(
            self._show,
            lambda message: message.text == Buttons.WORKER_SHOW_SERVICES.value)
        self.dispatcher.register_message_handler(
            self._input_name,
            lambda message: message.text == Buttons.WORKER_ADD_SERVICES.value)
        self.dispatcher.register_message_handler(
            self._add,
            state=ServiceStates.input_name,
            content_types=types.ContentTypes.TEXT)

    @staticmethod
    async def _show_actions(message: types.Message):
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup((
                Buttons.WORKER_SHOW_SERVICES.value,
                Buttons.WORKER_ADD_SERVICES.value,
                Buttons.WORKER_DELETE_SERVICES.value)))

    async def _show(self, message: types.Message):
        try:
            service_list = self.service_provider.get()
        except exceptions.ServiceIsNotFound as e:
            LoggerWrap().get_logger().exception(e)
            return

        reply_markup = types.InlineKeyboardMarkup()
        for service in service_list:
            reply_markup.add(types.InlineKeyboardButton(text=service.name, callback_data=service.name))

        await message.answer('Ваши услуги', reply_markup=reply_markup)

    @staticmethod
    async def _input_name(message: types.Message):
        await message.answer(static.INPUT_NAME)
        await ServiceStates.input_name.set()

    async def _add(self, message: types.Message, state: FSMContext):
        if ServiceInputValidator.is_valid_name(message.text):
            await message.reply(static.WRONG_INPUT)
            return

        service_name = message.text.title()
        try:
            self.service_provider.add(service_name)
        except exceptions.ServiceAlreadyExists:
            await message.reply(static.SERVICE_EXISTS)
            return

        await state.finish()
        await message.answer(f'{static.SERVICE_ADDED} {service_name}')
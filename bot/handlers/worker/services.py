from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from handlers.abstract_handler import AbstractHandler
from view import keyboard, static
from view.buttons import Buttons


class ServiceStates(StatesGroup):
    input_name = State()
    add = State()
    cancel = State()


class Services(AbstractHandler):
    BUTTON_PREFIX = 'svc_btn_'

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher)

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._show_actions,
            lambda message: message.text == Buttons.WORKER_SERVICES.value)
        self._dispatcher.register_message_handler(
            self._show,
            lambda message: message.text == Buttons.WORKER_SHOW_SERVICES.value)
        self._dispatcher.register_message_handler(
            self._input_name,
            lambda message: message.text == Buttons.WORKER_ADD_SERVICES.value)
        self._dispatcher.register_message_handler(
            self._add,
            state=ServiceStates.input_name,
            content_types=types.ContentTypes.TEXT)
        self._dispatcher.register_callback_query_handler(
            self._delete,
            lambda c: c.data and c.data.startswith(self.BUTTON_PREFIX))

    @staticmethod
    async def _show_actions(message: types.Message):
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup((
                Buttons.WORKER_SHOW_SERVICES.value,
                Buttons.WORKER_ADD_SERVICES.value,
                Buttons.WORKER_DELETE_SERVICES.value)))

    async def _show(self, message: types.Message):
        # try:
        #     service_list = self.service_provider.get()
        # except exceptions.ServiceIsNotFound as e:
        #     LoggerWrap().get_logger().exception(e)
        #     return
        #
        # reply_markup = types.InlineKeyboardMarkup()
        # for service in service_list:
        #     reply_markup.row(
        #         types.InlineKeyboardButton(text=service.name, callback_data=service.name),
        #         types.InlineKeyboardButton(
        #             text=f'☜ {Buttons.WORKER_DELETE_SERVICES.value}',
        #             callback_data=f'{self.BUTTON_PREFIX}{service.id}'))
        #
        # await message.answer('Ваши услуги', reply_markup=reply_markup)
        pass

    @staticmethod
    async def _input_name(message: types.Message):
        await message.answer(static.INPUT_NAME)
        await ServiceStates.input_name.set()

    async def _add(self, message: types.Message, state: FSMContext):
        # if ServiceInputValidator.is_valid_name(message.text):
        #     await message.reply(static.WRONG_INPUT)
        #     return
        #
        # service_name = message.text.title()
        # try:
        #     self.service_provider.add(service_name)
        # except exceptions.ServiceAlreadyExists:
        #     await message.reply(static.SERVICE_EXISTS)
        #     return
        #
        # await state.finish()
        # await message.answer(f'{static.SERVICE_ADDED} {service_name}')
        pass

    async def _delete(self, query: types.CallbackQuery):
        # service_id = query.data.removeprefix(self.BUTTON_PREFIX)
        await self._dispatcher.bot.send_message(
            query.message.chat.id,
            text='Нажата вторая кнопка',
            reply_markup=keyboard.create_reply_keyboard_markup((
                Buttons.WORKER_EDIT_SERVICES.value,
                Buttons.WORKER_DELETE_SERVICES.value)))

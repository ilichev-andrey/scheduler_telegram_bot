from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from wrappers import LoggerWrap

import exceptions
from handlers import states, handler
from handlers.abstract_handler import AbstractHandler
from managers.service import ServiceManager
from view import keyboard, static
from view.buttons import Buttons


class Services(AbstractHandler):
    BUTTON_PREFIX = 'svc_btn_'

    _service_manager: ServiceManager

    def __init__(self, dispatcher: Dispatcher, service_manager: ServiceManager):
        super().__init__(dispatcher)
        self._service_manager = service_manager

    def init(self) -> None:
        self._dispatcher.register_message_handler(
            self._show_actions,
            lambda message: message.text == Buttons.WORKER_SERVICES.value,
            state=states.WorkerStates.main_page
        )
        self._dispatcher.register_message_handler(
            self._show,
            lambda message: message.text == Buttons.WORKER_SHOW_SERVICES.value,
            state=states.ServiceStates.main_page
        )
        self._dispatcher.register_message_handler(
            self._input_name,
            lambda message: message.text == Buttons.WORKER_ADD_SERVICES.value,
            state=states.ServiceStates.input_name
        )
        self._dispatcher.register_message_handler(
            self._add,
            state=states.ServiceStates.add
        )

        self._dispatcher.register_callback_query_handler(
            self._delete,
            lambda callback_query: callback_query.data and callback_query.data.startswith(self.BUTTON_PREFIX),
            state=states.ServiceStates.show
        )

    @staticmethod
    async def _show_actions(message: types.Message):
        await states.ServiceStates.main_page.set()
        await message.answer(
            static.SELECT_ITEM,
            reply_markup=keyboard.create_reply_keyboard_markup((
                Buttons.WORKER_SHOW_SERVICES.value,
                Buttons.WORKER_ADD_SERVICES.value
            ))
        )

    async def _show(self, message: types.Message, state: FSMContext):
        try:
            service_list = await self._service_manager.get()
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        if not service_list:
            await message.answer(static.NO_SERVICES)
            await self._show_actions(message)
            return

        reply_markup = types.InlineKeyboardMarkup()
        for service in service_list:
            reply_markup.row(
                types.InlineKeyboardButton(text=service.name, callback_data=service.name),
                types.InlineKeyboardButton(
                    text=f'☜ {Buttons.WORKER_DELETE_SERVICES.value}',
                    callback_data=f'{self.BUTTON_PREFIX}{service.id}'))

        await states.ServiceStates.show.set()
        await message.answer(static.SERVICES, reply_markup=reply_markup)

    @staticmethod
    async def _input_name(message: types.Message):
        # await message.answer(static.INPUT_NAME)
        # await ServiceStates.input_name.set()
        pass

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
        message = query.message
        state = self._dispatcher.current_state()

        service_id = query.data.removeprefix(self.BUTTON_PREFIX)
        try:
            await self._service_manager.delete(service=frozenset((int(service_id),)))
        except exceptions.ApiCommandExecutionError as e:
            LoggerWrap().get_logger().exception(e)
            await message.answer(static.INTERNAL_ERROR)
            await handler.cancel(message, state)
            return

        await message.delete()
        await self._show(message, state)

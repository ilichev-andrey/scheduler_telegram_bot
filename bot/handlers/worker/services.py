from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from scheduler_core import containers

from bot import exceptions
from bot.handlers import states, handler
from bot.handlers.abstract_handler import AbstractHandler
from bot.managers.service import ServiceManager
from bot.view import keyboard, static
from bot.view.buttons import Buttons


class Services(AbstractHandler):
    _BUTTON_PREFIX = 'svc_btn_'

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
            state=states.ServiceStates.main_page
        )
        self._dispatcher.register_message_handler(
            self._input_execution_time,
            state=states.ServiceStates.input_execution_time
        )
        self._dispatcher.register_message_handler(
            self._add,
            state=states.ServiceStates.add
        )
        self._dispatcher.register_callback_query_handler(
            self._delete,
            lambda callback_query: callback_query.data and callback_query.data.startswith(self._BUTTON_PREFIX),
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
            await handler.error(str(e), message, state)
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
                    callback_data=f'{self._BUTTON_PREFIX}{service.id}'))

        await states.ServiceStates.show.set()
        await message.answer(
            static.SERVICES,
            reply_markup=keyboard.add_service_buttons_for_inline_keyboard(reply_markup)
        )

    @staticmethod
    async def _input_name(message: types.Message):
        await message.answer(static.INPUT_NAME)
        await states.ServiceStates.input_execution_time.set()

    @staticmethod
    async def _input_execution_time(message: types.Message, state: FSMContext):
        await state.update_data(data={'service_name': message.text})
        await message.answer(static.INPUT_EXECUTION_TIME)
        await states.ServiceStates.add.set()

    async def _add(self, message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            await message.reply(static.WRONG_INPUT)
            return

        user_data = await state.get_data()
        service = containers.Service(user_data['service_name'], message.text)
        try:
            await self._service_manager.add([service])
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        await message.answer(static.get_successful_add_service(service.name, service.execution_time_minutes))
        await states.ServiceStates.main_page.set()
        await self._show_actions(message)

    async def _delete(self, query: types.CallbackQuery):
        message = query.message
        state = self._dispatcher.current_state()

        service_id = query.data.removeprefix(self._BUTTON_PREFIX)
        try:
            await self._service_manager.delete(services=frozenset((int(service_id),)))
        except exceptions.ApiCommandExecutionError as e:
            await handler.error(str(e), message, state)
            return

        await message.delete()
        await self._show(message, state)

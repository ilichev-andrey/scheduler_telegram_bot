from typing import List

from aiogram import types
from scheduler_core import containers, enums
from scheduler_core.command_responses.add_user import AddUserResponse
from scheduler_core.command_responses.get_user import GetUserResponse
from scheduler_core.command_responses.get_workers import GetWorkersResponse
from scheduler_core.command_responses.update_user import UpdateUserResponse
from scheduler_core.commands.add_user import AddUserCommand
from scheduler_core.commands.get_user import GetUserCommand
from scheduler_core.commands.get_workers import GetWorkersCommand
from scheduler_core.commands.update_user import UpdateUserCommand

from bot import exceptions
from bot.managers.manager import Manager


class UserManager(Manager):
    async def add(self, tg_user: types.User) -> containers.User:
        """
        :raises:
            ApiCommandExecutionError если не удалось добавить пользователя
        """
        user = containers.User(
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            telegram_id=tg_user.id,
            telegram_name=tg_user.username
        )

        command = AddUserCommand(user=user)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, AddUserResponse):
                return response.user

        raise exceptions.ApiCommandExecutionError(
            f'Не удалось добавить пользователя по данным из telegram: {user}, response={response}'
        )

    async def get_user(self, tg_user: types.User) -> containers.User:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить пользователя
        """

        command = GetUserCommand(telegram_id=tg_user.id)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetUserResponse):
                return response.user
        if response.status == enums.CommandStatus.USER_IS_NOT_FOUND:
            return await self.add(tg_user)

        raise exceptions.ApiCommandExecutionError(
            f'Не удалось получить пользователя по данным из telegram: {tg_user}, response={response}'
        )

    async def get_workers(self) -> List[containers.User]:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить пользователя
        """

        response = await self._send_command(GetWorkersCommand())

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetWorkersResponse):
                return response.workers

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить работников. response={response}')

    async def update(self, user_id: int, phone_number: str):
        """
        :raises:
            ApiCommandExecutionError если не удалось обновить данные пользователя
        """

        response = await self._send_command(
            UpdateUserCommand(user=containers.User(id=user_id, phone_number=phone_number))
        )

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, UpdateUserResponse):
                return

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить работников. response={response}')


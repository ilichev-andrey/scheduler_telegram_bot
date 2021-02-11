from aiogram import types
from scheduler_core import configs, containers, enums, net
from scheduler_core.command_responses.get_user import GetUserResponse
from scheduler_core.commands.add_user import AddUserCommand
from scheduler_core.commands.get_user import GetUserCommand

import exceptions


class UserManager(object):
    _connection_config = configs.ConnectionConfig

    def __init__(self, api_connection: configs.ConnectionConfig):
        self._connection_config = api_connection

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
        response = await net.send_command(command, self._connection_config.host, self._connection_config.port)

        if response.status != enums.CommandStatus.SUCCESSFUL_EXECUTION:
            raise exceptions.ApiCommandExecutionError(f'Не удалось добавить пользователя по данным из telegram: {user}')

        return user

    async def get_user(self, tg_user: types.User) -> containers.User:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить пользователя
        """

        command = GetUserCommand(telegram_id=tg_user.id)
        response = await net.send_command(command, self._connection_config.host, self._connection_config.port)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetUserResponse):
                return response.user
        if response.status == enums.CommandStatus.USER_IS_NOT_FOUND:
            return await self.add(tg_user)

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить пользователя по данным из telegram: {tg_user}')

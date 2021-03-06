from scheduler_core import configs, net
from scheduler_core.command_responses.command_response import CommandResponse
from scheduler_core.commands.command import Command
from wrappers import LoggerWrap

from bot import exceptions


class Manager:
    _connection_config = configs.ConnectionConfig

    def __init__(self, api_connection: configs.ConnectionConfig):
        self._connection_config = api_connection

    async def _send_command(self, command: Command) -> CommandResponse:
        try:
            return await net.send_command(command, self._connection_config.host, self._connection_config.port)
        except OSError as e:
            LoggerWrap().get_logger().exception(str(e))
            raise exceptions.ApiCommandExecutionError(f'Не удалось отправить команду. command={command}')

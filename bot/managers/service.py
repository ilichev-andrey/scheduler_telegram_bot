from typing import FrozenSet, List

from scheduler_core import containers, enums
from scheduler_core.command_responses.get_services import GetServicesResponse
from scheduler_core.commands.delete_services import DeleteServicesCommand
from scheduler_core.commands.get_services import GetServicesCommand

import exceptions
from managers.manager import Manager


class ServiceManager(Manager):
    async def get(self) -> List[containers.Service]:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить услуги
        """

        command = GetServicesCommand()
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetServicesResponse):
                return response.services
        if response.status == enums.CommandStatus.NO_SERVICES_FOUND:
            return []

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить список услуг. response={response}')

    async def delete(self, service: FrozenSet[int]):
        """
        :raises:
            ApiCommandExecutionError если не удалось удалить услугу
        """

        command = DeleteServicesCommand(services=service)
        response = await self._send_command(command)

        if response.status != enums.CommandStatus.SUCCESSFUL_EXECUTION:
            raise exceptions.ApiCommandExecutionError(f'Не удалось получить список услуг. response={response}')

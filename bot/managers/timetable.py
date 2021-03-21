from datetime import date, time, datetime
from typing import FrozenSet, List

from scheduler_core import containers, enums
from scheduler_core.command_responses.add_timetable_slots import AddTimetableSlotsResponse
from scheduler_core.command_responses.get_client_timetable import GetClientTimetableResponse
from scheduler_core.command_responses.get_free_timetable_slots import GetFreeTimetableSlotsResponse
from scheduler_core.command_responses.get_worker_timetable import GetWorkerTimetableResponse
from scheduler_core.command_responses.release_timetable_slot import ReleaseTimetableSlotsResponse
from scheduler_core.command_responses.take_timetable_slots import TakeTimetableSlotsResponse
from scheduler_core.commands.add_timetable_slots import AddTimetableSlotsCommand
from scheduler_core.commands.get_client_timetable import GetClientTimetableCommand
from scheduler_core.commands.get_free_timetable_slots import GetFreeTimetableSlotsCommand
from scheduler_core.commands.get_worker_timetable import GetWorkerTimetableCommand
from scheduler_core.commands.release_timetable_slot import ReleaseTimetableSlotsCommand
from scheduler_core.commands.take_timetable_slots import TakeTimetableSlotsCommand

from bot import exceptions
from bot.managers.manager import Manager


class TimetableManager(Manager):
    async def add_slots(self, date_ranges: containers.DateRanges, times: List[time], worker_id: int) -> List[datetime]:
        """
        :raises:
            ApiCommandExecutionError если не удалось добавить слоты в расписание
        """

        command = AddTimetableSlotsCommand(date_ranges=date_ranges, times=times, worker=worker_id)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, AddTimetableSlotsResponse):
                return response.dates

        raise exceptions.ApiCommandExecutionError(f'Не удалось добавить слоты в расписание, response={response}')

    async def release_slots(self, entry_ids: FrozenSet[int]) -> List[containers.TimetableEntry]:
        """
        :raises:
            ApiCommandExecutionError если не удалось освободить слоты в расписании
        """

        command = ReleaseTimetableSlotsCommand(timetable_entries=entry_ids)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, ReleaseTimetableSlotsResponse):
                return response.timetable_entries

        raise exceptions.ApiCommandExecutionError(f'Не удалось освободить слоты в расписании, response={response}')

    async def get_free_slots(self, date_ranges: containers.DateRanges, services: FrozenSet[int],
                             worker_id: int) -> List[containers.TimetableEntry]:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить свободные слоты расписания
        """

        command = GetFreeTimetableSlotsCommand(date_ranges=date_ranges, services=services, worker=worker_id)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetFreeTimetableSlotsResponse):
                return response.timetable_entries
        if response.status == enums.CommandStatus.NO_FREE_SLOTS_FOUND:
            return []

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить расписание, response={response}')

    async def sign_up_client(self, entry_ids: FrozenSet[int], service_ids: FrozenSet[int], client_id: int) -> None:
        """
        :raises:
            ApiCommandExecutionError если не удалось зарегистрировать пользователя на услугу
        """

        command = TakeTimetableSlotsCommand(timetable_entries=entry_ids, services=service_ids, client=client_id)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, TakeTimetableSlotsResponse):
                return
        if response.status == enums.CommandStatus.SLOT_ALREADY_BUSY:
            raise exceptions.TimetableSlotAlreadyBusy()

        raise exceptions.ApiCommandExecutionError(f'Не удалось записать пользователя. response={response}')

    async def get_client_timetable(self, client_id: int) -> List[containers.TimetableEntry]:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить расписание клиента
        """

        command = GetClientTimetableCommand(client=client_id, limit=10)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetClientTimetableResponse):
                return response.timetable_entries
        if response.status == enums.CommandStatus.NO_TIMETABLE_ENTRIES_FOUND:
            raise exceptions.EmptyTimetable()

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить расписание клиента. response={response}')

    async def get_worker_timetable(self, worker_id: int, time_type: enums.TimeType,
                                   time_limit: enums.TimeLimit) -> List[containers.TimetableEntry]:
        """
        :raises:
            ApiCommandExecutionError если не удалось получить расписание работника
        """

        command = GetWorkerTimetableCommand(worker=worker_id, time_type=time_type, time_limit=time_limit)
        response = await self._send_command(command)

        if response.status == enums.CommandStatus.SUCCESSFUL_EXECUTION:
            if isinstance(response, GetWorkerTimetableResponse):
                return response.timetable_entries
        if response.status == enums.CommandStatus.NO_TIMETABLE_ENTRIES_FOUND:
            raise exceptions.EmptyTimetable()

        raise exceptions.ApiCommandExecutionError(f'Не удалось получить расписание работника. response={response}')

    @staticmethod
    def filter_by_day(entries: List[containers.TimetableEntry], day: date) -> List[containers.TimetableEntry]:
        return [entry for entry in entries if entry.start_dt.date() == day]

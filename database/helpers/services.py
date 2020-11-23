from typing import List

from database.exceptions import ServiceIsNotFound
from database.containers import Service


def get_by_name(services: List[Service], name: str) -> Service:
    for service in services:
        if service.name == name:
            return service

    raise ServiceIsNotFound(f'Услуга не найдена {name}', services)


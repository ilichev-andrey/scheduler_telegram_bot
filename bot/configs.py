from typing import NamedTuple, Dict

from scheduler_core.configs import ConnectionConfig


class Config(NamedTuple):
    log_file: str
    api_connection: ConnectionConfig


def load_config(data: Dict) -> Config:
    """
    :raises
        KeyError если отсутствует параметр в конфиге
    """

    connection_data = data['api_connection']
    return Config(
        log_file=data['log_file'],
        api_connection=ConnectionConfig(host=connection_data['host'], port=connection_data['port'])
    )

import json
import os
from typing import NamedTuple, Dict

from scheduler_core.configs import ConnectionConfig


class Config(NamedTuple):
    log_file: str
    api_connection: ConnectionConfig
    telegram_api_token: str


def create_config(data: Dict) -> Config:
    """
    :raises
        KeyError если отсутствует параметр
        ValueError если указано несоответствующее значение параметра
    """

    connection_data = data['api_connection']
    return Config(
        log_file=str(data['log_file']),
        api_connection=ConnectionConfig(host=str(connection_data['host']), port=int(connection_data['port'])),
        telegram_api_token=str(data['telegram_api_token'])
    )


def load_from_env() -> Config:
    """
    :raises
        KeyError если отсутствует параметр в переменных окружения
        ValueError если указано несоответствующее значение параметра
    """

    return Config(
        log_file=str(os.environ['LOG_FILE']),
        api_connection=ConnectionConfig(
            host=str(os.environ['API_CONNECTION_HOST']),
            port=int(os.environ['API_CONNECTION_PORT'])
        ),
        telegram_api_token=str(os.environ['TELEGRAM_API_TOKEN'])
    )


def load_from_file(config_file: str) -> Config:
    """
    :raises
        KeyError если отсутствует параметр в конфиге
        ValueError если указано несоответствующее значение параметра
    """

    with open(config_file) as fin:
        config = json.load(fin)

    return create_config(config)


def load(config_file: str) -> Config:
    """
    :raises
        KeyError если отсутствует параметр
        ValueError если указано несоответствующее значение параметра
    """

    if os.path.isfile(config_file):
        return load_from_file(config_file)

    return load_from_env()

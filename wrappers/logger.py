import os
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import AnyStr


class LoggerWrap(object):
    __log_name: AnyStr = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoggerWrap, cls).__new__(cls)
        return cls.instance

    def set_log_name(self, log_name: AnyStr):
        self.__log_name = log_name

    def get_logger(self) -> logging.Logger:
        return logging.getLogger(self.__log_name)


def __get_default_formatter() -> logging.Formatter:
    return logging.Formatter("[{asctime}] [{filename}::{funcName}::{lineno}] [{levelname}] {message}", style='{')


def __get_default_handler(name: AnyStr, formatter: logging.Formatter, backup_count=5) -> TimedRotatingFileHandler:
    file_handler = TimedRotatingFileHandler(name, when='midnight', backupCount=backup_count)
    file_handler.setFormatter(formatter)
    return file_handler


def __create_file(name: AnyStr) -> AnyStr:
    file_name = os.path.abspath(name)
    log_dir = os.path.dirname(file_name)
    os.makedirs(log_dir, exist_ok=True)

    with open(file_name, 'w+') as fin:
        fin.write('')

    return file_name


def create(name: str, level: int, handler=None, formatter=None) -> LoggerWrap:
    file_name = __create_file(name)

    if formatter is None:
        formatter = __get_default_formatter()

    if handler is None:
        handler = __get_default_handler(file_name, formatter)

    logger = logging.getLogger(file_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    logger_wrap = LoggerWrap()
    logger_wrap.set_log_name(file_name)
    return logger_wrap

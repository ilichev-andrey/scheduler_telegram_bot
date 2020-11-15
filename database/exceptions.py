class BaseBotException(Exception):
    pass


class UserIsNotFound(BaseBotException):
    """Если пользователь не существует"""
    pass


class ServiceIsNotFound(BaseBotException):
    """Если услуга не существует"""
    pass


class TimetableEntryIsNotFound(BaseBotException):
    """Если запись в расписании не существует"""
    pass

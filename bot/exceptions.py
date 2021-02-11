class BaseBotException(Exception):
    """Базовое исключение для данного проекта"""
    pass


class ApiCommandExecutionError(BaseBotException):
    """Не удалось выполнить команду в другом модуле, отправленную через API"""
    pass

class BaseBotException(Exception):
    pass


class UserIsNotFound(BaseBotException):
    """Если пользователь не существует"""
    pass



class ServiceInputValidator(object):
    @staticmethod
    def is_valid_name(name: str):
        return any(map(str.isdigit, name))

class Error(Exception):  # ошибочки для паролей и логинов
    pass


class LengthError(Error):
    pass


class LoginAlreadyExists(Error):
    pass


class RussianCharError(Error):
    pass


class CapitalLetterError(Error):
    pass


class NumberError(Error):
    pass


class SpecialCharError(Error):
    pass


class PasswordsAreNotMatchingError(Error):
    pass


class DifferentPassword(Error):
    pass

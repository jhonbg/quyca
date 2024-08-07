class ORMError(Exception):
    """
    Any exception captured from the orm
    """


class NoObserverRegister(Exception):
    """
    Exception when observer is not registered
    """

    def __init__(self, service: str) -> None:
        self.service = service


class InvalidCredentials(Exception):
    """
    Exception for invalid credentials
    """

    def __init__(self, msg: str | None) -> None:
        self.msg = msg

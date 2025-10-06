from abc import ABC, abstractmethod


class IStaffRepository(ABC):
    """
    Checks if a user's token is valid.
    """

    @abstractmethod
    def is_token_valid(self, email: str, token: str) -> bool:
        pass

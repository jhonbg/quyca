from domain.repositories.staff_repository_interface import IStaffRepository


class StaffRepository(IStaffRepository):
    def __init__(self, db):
        self.collection = db["users"]

    """Checks if a users token is valid by comparing with the database"""

    def is_token_valid(self, email: str, token: str) -> bool:
        user = self.collection.find_one({"email": email.strip().lower()})
        return user and user.get("token") == token

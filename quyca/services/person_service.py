from models.person_model import Person
from repositories.person_repository import PersonRepository


class PersonService:
    @staticmethod
    def get_by_id(person_id: str) -> Person:
        return PersonRepository.get_by_id(person_id)
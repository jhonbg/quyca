from bson import ObjectId

from exceptions.person_exception import PersonException
from models.person_model import Person
from repositories.mongo import database


class PersonRepository:
    person_collection = database["person"]

    @staticmethod
    def get_by_id(person_id: str) -> Person:
        person_data = PersonRepository.person_collection.find_one({"_id": ObjectId(person_id)})

        if person_data is None:
            raise PersonException(person_id)

        return Person(**person_data)

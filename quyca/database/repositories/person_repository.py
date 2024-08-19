from bson import ObjectId

from database.generators.person_generator import PersonGenerator
from exceptions.person_exception import PersonException
from database.models.person_model import Person
from database.repositories.calculations_repository import CalculationsRepository
from database.mongo import database
from database.repositories.work_repository import WorkRepository


class PersonRepository:
    person_collection = database["person"]

    @staticmethod
    def get_by_id(person_id: str) -> Person:
        person_data = PersonRepository.person_collection.find_one({"_id": ObjectId(person_id)})

        if person_data is None:
            raise PersonException(person_id)

        person_calculations = CalculationsRepository.get_person_calculations(person_id)
        person = Person(**person_data)

        person.citations_count = person_calculations.citations_count
        person.products_count = WorkRepository.get_works_count_by_person(person_id)

        return person

    @staticmethod
    def get_persons_by_affiliation(affiliation_id: str) -> list:
        pipeline = [
            {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
            {"$project": {"full_name": 1}},
        ]

        cursor = database["person"].aggregate(pipeline)

        return PersonGenerator.get(cursor)

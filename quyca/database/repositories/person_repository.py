from bson import ObjectId

from database.generators import person_generator
from exceptions.person_exception import PersonException
from database.models.person_model import Person
from database.mongo import database


def get_person_by_id(person_id: str) -> Person:
    person_data = database["person"].find_one({"_id": ObjectId(person_id)})
    if not person_data:
        raise PersonException(person_id)
    return Person(**person_data)


def get_persons_by_affiliation(affiliation_id: str) -> list:
    pipeline = [
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"full_name": 1}},
    ]
    cursor = database["person"].aggregate(pipeline)
    return person_generator.get(cursor)

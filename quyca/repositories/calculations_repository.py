from typing import List, Optional

from bson import ObjectId

from models.person_calculations_model import PersonCalculations
from repositories.mongo import calculations_database


class CalculationsRepository:
    person_calculations_collection = calculations_database["person"]

    @staticmethod
    def get_person_calculations_by_person_id(person_id: str) -> PersonCalculations:
        person_calculations = CalculationsRepository.person_calculations_collection.find_one({"_id": ObjectId(person_id)})

        return PersonCalculations(**person_calculations)
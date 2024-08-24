from bson import ObjectId

from database.models.affiliation_calculations_model import AffiliationCalculations
from database.models.person_calculations_model import PersonCalculations
from database.mongo import calculations_database
from exceptions.affiliation_calculations_exception import AffiliationCalculationsException
from exceptions.person_calculations_exception import PersonCalculationsException


class CalculationsRepository:

    @staticmethod
    def get_person_calculations(person_id: str) -> PersonCalculations:
        person_calculations = calculations_database["person"].find_one({"_id": ObjectId(person_id)})

        if not person_calculations:
            raise PersonCalculationsException(person_id)

        return PersonCalculations(**person_calculations)

    @staticmethod
    def get_affiliation_calculations(affiliation_id: str) -> AffiliationCalculations:
        affiliation_calculations = calculations_database["affiliations"].find_one({"_id": ObjectId(affiliation_id)})

        if not affiliation_calculations:
            raise AffiliationCalculationsException(affiliation_id)

        return AffiliationCalculations(**affiliation_calculations)
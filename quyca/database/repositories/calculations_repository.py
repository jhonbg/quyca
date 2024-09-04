from bson import ObjectId

from database.models.affiliation_calculations_model import AffiliationCalculations
from database.models.base_model import CitationsCount
from database.models.person_calculations_model import PersonCalculations
from database.mongo import calculations_database


def get_person_calculations(person_id: str) -> PersonCalculations:
    person_calculations = calculations_database["person"].find_one(
        {"_id": ObjectId(person_id)}
    )

    if not person_calculations:
        return PersonCalculations()
        # raise PersonCalculationsException(person_id)

    return PersonCalculations(**person_calculations)


def get_affiliation_calculations(affiliation_id: str) -> AffiliationCalculations:
    affiliation_calculations = calculations_database["affiliations"].find_one(
        {"_id": ObjectId(affiliation_id)}
    )

    if not affiliation_calculations:
        return AffiliationCalculations()
        # raise AffiliationCalculationsException(affiliation_id)

    return AffiliationCalculations(**affiliation_calculations)


def get_citations_count_by_affiliation(affiliation_id: str) -> list[CitationsCount]:
    affiliation_calculations = get_affiliation_calculations(affiliation_id)
    return affiliation_calculations.citations_count

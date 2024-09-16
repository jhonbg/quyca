from typing import Generator, Tuple

from bson import ObjectId

from database.generators import person_generator
from database.models.base_model import QueryParams
from database.repositories import base_repository
from exceptions.not_entity_exception import NotEntityException
from database.models.person_model import Person
from database.mongo import database


def get_person_by_id(person_id: str) -> Person:
    person_data = database["person"].find_one({"_id": ObjectId(person_id)})
    if not person_data:
        raise NotEntityException(f"The person with id {person_id} does not exist.")
    return Person(**person_data)


def get_persons_by_affiliation(affiliation_id: str) -> list:
    pipeline = [
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1, "full_name": 1}},
    ]
    cursor = database["person"].aggregate(pipeline)
    return person_generator.get(cursor)


def search_persons(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    persons = database["person"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return person_generator.get(persons), total_results

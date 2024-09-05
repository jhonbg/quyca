from typing import Generator

from bson import ObjectId

from database.generators import person_generator
from database.models.base_model import QueryParams
from database.repositories import base_repository
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


def search_persons(
    query_params: QueryParams, pipeline_params: dict | None = None
) -> (Generator, int):
    if pipeline_params is None:
        pipeline_params = {}
    pipeline, count_pipeline = base_repository.get_search_pipelines(
        query_params, pipeline_params
    )
    pipeline = (
        pipeline[:2]
        + [
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "authors.id",
                    "as": "works",
                    "pipeline": [{"$count": "count"}],
                }
            },
            {
                "$addFields": {
                    "products_count": {
                        "$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]
                    },
                }
            },
            {"$project": {"works": 0}},
        ]
        + pipeline[2:]
    )
    persons = database["person"].aggregate(pipeline)
    total_results = next(
        database["person"].aggregate(count_pipeline), {"total_results": 0}
    )["total_results"]
    return person_generator.get(persons), total_results

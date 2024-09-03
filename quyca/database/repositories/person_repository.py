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


def search_person(
    query_params: QueryParams, pipeline_params: dict | None = None
) -> (Generator, int):
    if pipeline_params is None:
        pipeline_params = {}
    pipeline, count_pipeline = base_repository.get_search_pipelines(
        query_params, pipeline_params
    )
    pipeline += [
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "count",
                "pipeline": [{"$count": "count"}],
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "works",
                "pipeline": [
                    {"$unwind": "$citations_count"},
                    {
                        "$group": {
                            "_id": "$_id",
                            "citations_count_openalex": {
                                "$sum": {
                                    "$cond": [
                                        {
                                            "$eq": [
                                                "$citations_count.source",
                                                "openalex",
                                            ]
                                        },
                                        "$citations_count.count",
                                        0,
                                    ]
                                }
                            },
                            "citations_count_scholar": {
                                "$sum": {
                                    "$cond": [
                                        {"$eq": ["$citations_count.source", "scholar"]},
                                        "$citations_count.count",
                                        0,
                                    ]
                                }
                            },
                        }
                    },
                ],
            }
        },
        {
            "$addFields": {
                "products_count": {
                    "$ifNull": [{"$arrayElemAt": ["$count.count", 0]}, 0]
                },
                "citations_count": [
                    {
                        "count": {
                            "$ifNull": [
                                {
                                    "$arrayElemAt": [
                                        "$works.citations_count_openalex",
                                        0,
                                    ]
                                },
                                0,
                            ]
                        },
                        "source": "openalex",
                    },
                    {
                        "count": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$works.citations_count_scholar", 0]},
                                0,
                            ]
                        },
                        "source": "scholar",
                    },
                ],
            }
        },
        {"$project": {"works": 0, "count": 0}},
    ]
    persons = database["person"].aggregate(pipeline)
    total_results = next(
        database["person"].aggregate(count_pipeline), {"total_results": 0}
    )["total_results"]
    return person_generator.get(persons), total_results

from typing import Generator, Tuple

from bson import ObjectId

from database.generators import source_generator
from database.generators import work_generator
from database.models.base_model import QueryParams
from database.models.work_model import Work
from database.repositories import base_repository
from database.mongo import database
from exceptions.not_entity_exception import NotEntityException


def get_work_by_id(work_id: str) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise NotEntityException(f"The work with id {work_id} does not exist.")
    return Work(**work)


def get_works_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            },
        },
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    base_repository.set_pagination(pipeline, query_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_affiliation(affiliation_id: str) -> int:
    pipeline = get_works_by_affiliation_pipeline(affiliation_id)
    pipeline += [{"$count": "total"}]
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_works_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_person(person_id: str) -> int:
    pipeline = [{"$match": {"authors.id": ObjectId(person_id)}}, {"$count": "total"}]
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_works(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    works = database["works"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return work_generator.get(works), total_results


def get_sources_by_affiliation(affiliation_id: str, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_sources_by_affiliation_pipeline(affiliation_id)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    project = pipeline_params.get("project")
    if project and "ranking" in project:
        pipeline += [
            {
                "$addFields": {
                    "ranking": {
                        "$filter": {
                            "input": "$ranking",
                            "as": "rank",
                            "cond": {
                                "$and": [
                                    {"$lte": ["$$rank.from_date", "$date_published"]},
                                    {"$gte": ["$$rank.to_date", "$date_published"]},
                                ]
                            },
                        }
                    }
                }
            },
        ]
    base_repository.set_project(pipeline, project)
    cursor = database["works"].aggregate(pipeline)
    return source_generator.get(cursor)


def get_sources_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_sources_by_person_pipeline(person_id)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return source_generator.get(cursor)


def get_works_by_affiliation_pipeline(affiliation_id: str) -> list:
    return [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            },
        },
    ]


def get_sources_by_affiliation_pipeline(affiliation_id: str) -> list:
    pipeline = get_works_by_affiliation_pipeline(affiliation_id)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": "$year_published",
                "source.date_published": "$date_published",
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    return pipeline


def get_sources_by_person_pipeline(person_id: str) -> list:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": "$year_published",
                "source.date_published": "$date_published",
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    return pipeline

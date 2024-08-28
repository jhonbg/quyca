from typing import Optional, Any, Generator

from bson import ObjectId
from werkzeug.datastructures.structures import MultiDict

from core.config import settings
from database.generators import source_generator
from database.generators import work_generator
from database.models.base_model import CitationsCount
from database.models.work_model import Work
from database.repositories import calculations_repository
from database.mongo import database
from exceptions.work_exception import WorkException


def get_work_by_id(work_id: id) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise WorkException(work_id)
    return Work(**work)

def get_works_by_affiliation(
        affiliation_id: str,
        affiliation_type: str,
        query_params: MultiDict | None = None,
        pipeline_params: dict | None = None
) -> Generator:
    if query_params is None:
        query_params = {}
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"
    if collection == "affiliations":
        pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]
    pipeline = process_params(pipeline, query_params, pipeline_params)
    cursor = database[collection].aggregate(pipeline)
    return work_generator.get(cursor)

def get_sources_by_affiliation(
        affiliation_id: str,
        affiliation_type: str,
        pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"
    pipeline = get_sources_by_affiliation_pipeline(affiliation_id, affiliation_type)
    if match_param := pipeline_params.get("match"):
        pipeline += [{"$match": match_param}]
    project = pipeline_params["project"]
    if "ranking" in project:
        pipeline += [
            {
                "$addFields": {
                    "ranking": {
                        "$filter": {
                            "input": "$ranking",
                            "as": "rank",
                            "cond": {
                                "$and": [
                                    {"$lte": ["$$rank.from_date","$date_published"]},
                                    {"$gte": ["$$rank.to_date", "$date_published"]},
                                ]
                            },
                        }
                    }
                }
            },
        ]
    pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]
    cursor = database[collection].aggregate(pipeline)
    return source_generator.get(cursor)

def get_works_count_by_affiliation(
        affiliation_id: str, affiliation_type: str, filters: dict | None = None
) -> int:
    affiliation_type = "institution" if affiliation_type in settings.institutions else affiliation_type
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    collection = "affiliations" if affiliation_type in ["department", "faculty"] else "works"
    if collection == "affiliations":
        pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]
    if filters:
        pipeline += get_filter_list(filters)
    pipeline += [{"$count": "total"}]
    works_count = next(database[collection].aggregate(pipeline), {"total": 0}).get("total", 0)
    return works_count

def get_citations_count_by_affiliation(affiliation_id: str) -> list[CitationsCount]:
    affiliation_calculations = calculations_repository.get_affiliation_calculations(affiliation_id)
    return affiliation_calculations.citations_count

def get_sources_by_related_affiliation(
        affiliation_id: str, affiliation_type: str, relation_type: str, pipeline_params: dict | None = None
) -> Generator:
    from database.repositories import affiliation_repository
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = affiliation_repository.get_related_affiliations_by_type_pipeline(
        affiliation_id, affiliation_type, relation_type
    )
    pipeline += [{"$project": {"id": 1, "names": 1}}]
    if relation_type == "group":
        pipeline += [
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "groups.id",
                    "as": "works",
                }
            }
        ]
    else:
        pipeline += [
            {
                "$lookup": {
                    "from": "person",
                    "localField": "_id",
                    "foreignField": "affiliations.id",
                    "as": "authors",
                },
            },
            {"$unwind": "$authors"},
            {
                "$project": {
                    "authors_id": "$authors._id",
                    "id": 1,
                    "names": 1,
                },
            },
            {
                "$lookup": {
                    "from": "works",
                    "localField": "authors_id",
                    "foreignField": "authors.id",
                    "as": "works",
                },
            },
        ]
    pipeline += [
        {"$unwind": "$works"},
        {
            "$lookup": {
                "from": "sources",
                "localField": "works.source.id",
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": "$works.year_published",
                "source.date_published": "$works.date_published",
                "source.affiliation_names": "$names",
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    project = pipeline_params.get("project")
    if project:
        if "ranking" in pipeline_params["project"]:
            pipeline += [
                {
                    "$addFields": {
                        "ranking": {
                            "$filter": {
                                "input": "$ranking",
                                "as": "rank",
                                "cond": {
                                    "$and": [
                                        {
                                            "$lte": [
                                                "$$rank.from_date",
                                                "$date_published",
                                            ]
                                        },
                                        {"$gte": ["$$rank.to_date", "$date_published"]},
                                    ]
                                },
                            }
                        }
                    }
                },
            ]
        pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]
    sources = database["affiliations"].aggregate(pipeline)
    return source_generator.get(sources)

def get_works_by_person(
        person_id: str,
        query_params: MultiDict | None = None,
        pipeline_params: dict = None
) -> Generator:
    if query_params is None:
        query_params = {}
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    pipeline = process_params(pipeline, query_params, pipeline_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)

def get_works_count_by_person(person_id) -> Optional[int]:
    return database["works"].aggregate([
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$count": "total"}
    ]).next().get("total", 0)

def get_sources_by_person(person_id: str, query_params, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = get_sources_by_person_pipeline(person_id)
    pipeline = process_params(pipeline, query_params, pipeline_params)
    cursor = database["works"].aggregate(pipeline)
    return source_generator.get(cursor)

def get_works_by_affiliation_pipeline(affiliation_id: str, affiliation_type: str):
    if affiliation_type == "institution":
        pipeline = [
            {
                "$match": {
                    "authors.affiliations.id": ObjectId(affiliation_id),
                },
            },
        ]
        return pipeline
    if affiliation_type == "group":
        pipeline = [
            {
                "$match": {
                    "groups.id": ObjectId(affiliation_id),
                },
            },
        ]
        return pipeline
    pipeline = [
        {"$match": {"_id": ObjectId(affiliation_id)}},
        {"$project": {"relations.types.type": 1, "relations.id": 1}},
        {"$unwind": "$relations"},
        {"$match": {"relations.types.type": "Education"}},
        {
            "$lookup": {
                "from": "person",
                "localField": "_id",
                "foreignField": "affiliations.id",
                "as": "person",
                "pipeline": [{"$project": {"id": 1, "full_name": 1}}],
            }
        },
        {"$unwind": "$person"},
        {
            "$lookup": {
                "from": "works",
                "localField": "person._id",
                "foreignField": "authors.id",
                "as": "work",
                "pipeline": [{"$project": {"authors": 1}}],
            }
        },
        {"$unwind": "$work"},
        {"$unwind": "$work.authors"},
        {"$match": {"$expr": {"$eq": ["$person._id", "$work.authors.id"]}}},
        {"$unwind": "$work.authors.affiliations"},
        {"$match": {"$expr": {"$eq": ["$relations.id", "$work.authors.affiliations.id"]}}},
        {"$group": {"_id": "$work._id", "work": {"$first": "$work"}}},
        {"$project": {"work._id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "work._id",
                "foreignField": "_id",
                "as": "works",
            }
        },
        {"$unwind": "$works"},
    ]
    return pipeline

def get_sources_by_affiliation_pipeline(affiliation_id, affiliation_type):
    pipeline = get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
    is_person = True if affiliation_type in ["faculty", "department"] else False
    pipeline += [
        {
            "$lookup": {
                "from": "sources",
                "localField": ("works.source.id" if is_person else "source.id"),
                "foreignField": "_id",
                "as": "source",
            }
        },
        {"$unwind": "$source"},
        {
            "$addFields": {
                "source.apc.year_published": (
                    "$works.year_published" if is_person else "$year_published"
                ),
                "source.date_published": (
                    "$works.date_published" if is_person else "$date_published"
                ),
            }
        },
        {"$replaceRoot": {"newRoot": "$source"}},
    ]
    return pipeline

def get_sources_by_person_pipeline(person_id):
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

def process_params(pipeline, query_params, pipeline_params: dict | None = None):
    if pipeline_params is None:
        pipeline_params = {}
    if sort := query_params.get("sort"):
        pipeline += get_sort(sort)
    if match_param := pipeline_params.get("match"):
        pipeline += [{"$match": match_param}]
    if project_param := pipeline_params.get("project"):
        pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project_param}}}]
    if limit_param := pipeline_params.get("limit"):
        pipeline += [{"$limit": limit_param}]
    if skip_param := pipeline_params.get("skip"):
        pipeline += [{"$skip": skip_param}]
    return pipeline

def get_sort(sort: str) -> list[dict]:
    sort_field, direction = (sort[:-1], -1) if sort.endswith("-") else (sort, 1)
    sort_translation: dict[str, str] = {
        "citations": "citations_count.count",
        "year": "year_published",
        "title": "titles.0.title",
        "alphabetical": "titles.0.title",
    }
    source_priority = {
        "openalex": 1,
        "scholar": 2,
        "scienti": 3,
        "minciencias": 4,
        "ranking": 5,
    }
    pipeline = []
    if sort_field == "year":
        pipeline += [{"$match": {"year_published": {"$ne": None}}}]
    if sort_field in ["title", "alphabetical"]:
        pipeline += [
            {
                "$addFields": {
                    "source_priority": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$eq": ["$titles.0.source", "openalex"]
                                    },
                                    "then": source_priority["openalex"],
                                },
                                {
                                    "case": {
                                        "$eq": ["$titles.0.source", "scholar"]
                                    },
                                    "then": source_priority["scholar"],
                                },
                                {
                                    "case": {
                                        "$eq": ["$titles.0.source", "scienti"]
                                    },
                                    "then": source_priority["scienti"],
                                },
                                {
                                    "case": {
                                        "$eq": ["$titles.0.source", "minciencias"]
                                    },
                                    "then": source_priority["minciencias"],
                                },
                                {
                                    "case": {
                                        "$eq": ["$titles.0.source", "ranking"]
                                    },
                                    "then": source_priority["ranking"],
                                },
                            ],
                            "default": 6,
                        }
                    },
                    "normalized_titles": {
                        "$map": {
                            "input": "$titles",
                            "as": "title",
                            "in": {
                                "title": {"$toLower": "$$title.title"},
                                "source": "$$title.source",
                            },
                        }
                    },
                }
            },
            {
                "$sort": {
                    "source_priority": 1,
                    "normalized_titles.0.title": direction,
                    "_id": -1,
                }
            },
        ]
    else:
        pipeline += [
            {
                "$sort": {
                    sort_translation.get(sort_field, "titles.0.title"): direction,
                    "_id": -1,
                }
            }
        ]
    return pipeline

def filter_translation(value: Any) -> dict[str, Any]:
    return {
        "type": {"$match": {"types.type": value}},
        "start_year": {"$match": {"year_published": {"$gte": value}}},
        "end_year": {"$match": {"year_published": {"$lte": value}}},
    }

def get_filter_list(filters: dict[str, Any]) -> list[dict[str, Any]]:
    filter_list = []
    for key, value in filters.items():
        if value:
            filter_list += [filter_translation(value)[key]]
    return filter_list

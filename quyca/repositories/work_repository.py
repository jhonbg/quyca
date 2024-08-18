from typing import Optional, Any, Generator

from bson import ObjectId
from werkzeug.datastructures.structures import MultiDict

from core.config import settings
from generators.source_generator import SourceGenerator
from generators.work_generator import WorkGenerator
from models.base_model import CitationsCount
from repositories.affiliation_repository import AffiliationRepository
from repositories.calculations_repository import CalculationsRepository
from repositories.mongo import database


class WorkRepository:
    work_collection = database["works"]

    @classmethod
    def get_works_by_affiliation_pipeline(cls, affiliation_id: str, affiliation_type: str):
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

    @classmethod
    def get_sort(cls, sort: str) -> list[dict]:
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

    @staticmethod
    def get_works_count_by_person_id(person_id) -> Optional[int]:
        return WorkRepository.work_collection.aggregate([
            {"$match": {"authors.id": ObjectId(person_id)}},
            {"$count": "total"}
        ]).next().get("total", 0)

    @classmethod
    def get_works_by_affiliation(
            cls,
            affiliation_id: str,
            affiliation_type: str,
            query_params: MultiDict,
            pipeline_params=None
    ) -> Generator:

        if pipeline_params is None:
            pipeline_params = {}
        pipeline = cls.get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
        collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"

        if collection == "affiliations":
            pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]

        if sort := query_params.get("sort"):
            pipeline += cls.get_sort(sort)

        if match_param := pipeline_params.get("match"):
            pipeline += [{"$match": match_param}]

        if project_param := pipeline_params.get("project"):
            pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project_param}}}]

        if limit_param := pipeline_params.get("limit"):
            pipeline += [{"$limit": limit_param}]

        if skip_param := pipeline_params.get("skip"):
            pipeline += [{"$skip": skip_param}]

        cursor = database[collection].aggregate(pipeline)

        return WorkGenerator.get(cursor)

    @classmethod
    def get_sources_by_affiliation(
            cls,
            affiliation_id: str,
            affiliation_type: str,
            pipeline_params: dict = dict
    ) -> Generator:

        collection = "affiliations" if affiliation_type in ["faculty", "department"] else "works"

        pipeline = cls.get_sources_by_affiliation_pipeline(affiliation_id, affiliation_type)

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

        return SourceGenerator.get(cursor)


    @classmethod
    def get_sources_by_affiliation_pipeline(cls, affiliation_id, affiliation_type):
        pipeline = cls.get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)

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


    @staticmethod
    def get_citations_count_by_affiliation(affiliation_id: str) -> list[CitationsCount]:

        affiliation_calculations = CalculationsRepository.get_affiliation_calculations(affiliation_id)

        return affiliation_calculations.citations_count


    @classmethod
    def count_papers(cls, affiliation_id: str, affiliation_type: str, filters: dict[str, Any] = None) -> int:
        affiliation_type = "institution" if affiliation_type in settings.institutions else affiliation_type
        pipeline = cls.get_works_by_affiliation_pipeline(affiliation_id, affiliation_type)
        collection = "affiliation" if affiliation_type not in ["department", "faculty"] else "work"

        if collection == "affiliations":
            pipeline += [{"$replaceRoot": {"newRoot": "$works"}}]

        if filters:
            pipeline += cls.get_filter_list(filters)

        pipeline += [{"$count": "total"}]

        works_count = next(database[collection].aggregate(pipeline), {"total": 0}).get("total", 0)

        return works_count


    @staticmethod
    def filter_translation(value: Any) -> dict[str, Any]:
        return {
            "type": {"$match": {"types.type": value}},
            "start_year": {"$match": {"year_published": {"$gte": value}}},
            "end_year": {"$match": {"year_published": {"$lte": value}}},
        }


    @classmethod
    def get_filter_list(cls, filters: dict[str, Any]) -> list[dict[str, Any]]:
        filter_list = []

        for key, value in filters.items():
            if value:
                filter_list += [cls.filter_translation(value)[key]]

        return filter_list


    @staticmethod
    def get_sources_by_related_affiliation(affiliation_id: str, relation_type: str, pipeline_params: dict) -> Generator:
        pipeline = AffiliationRepository.get_related_affiliations_by_type_pipeline(affiliation_id, relation_type)

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

        return SourceGenerator.get(sources)
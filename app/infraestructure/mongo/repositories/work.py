from typing import Any, Iterable

from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine
from infraestructure.mongo.utils.iterators import WorkIterator, SourceIterator
from schemas.work import WorkCsv, WorkListApp
from core.config import settings


class WorkRepository(RepositoryBase[Work, WorkIterator]):
    @classmethod
    def wrap_pipeline(
        cls, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, Any]]:
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
            {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
            {"$project": {"affiliations": 1, "full_name": 1, "_id": 1}},
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "authors.id",
                    "as": "works",
                }
            },
            # affiliation start and end data"}
            {"$unwind": "$works"},
            # {
            #     "$addFields": {
            #         "current_affiliation": {
            #             "$arrayElemAt": [
            #                 {
            #                     "$filter": {
            #                         "input": "$affiliations",
            #                         "as": "aff",
            #                         "cond": {
            #                             "$eq": [
            #                                 "$$aff.id",
            #                                 ObjectId(affiliation_id),
            #                             ]
            #                         },
            #                     }
            #                 },
            #                 0,
            #             ]
            #         }
            #     }
            # },
            # {
            #     "$addFields": {
            #         "start_date": "$current_affiliation.start_date",
            #         "end_date": {
            #             "$cond": {
            #                 "if": {"$eq": ["$current_affiliation.end_date", -1]},
            #                 "then": "$$NOW",
            #                 "else": "$current_affiliation.end_date",
            #             }
            #         },
            #     }
            # },
            # {
            #     "$match": {
            #         "$expr": {
            #             "$and": [
            #                 {"$gte": ["$works.date_published", "$start_date"]},
            #                 {"$lte": ["$works.date_published", "$end_date"]},
            #             ]
            #         }
            #     }
            # },
            {"$group": {"_id": "$works._id", "works": {"$first": "$works"}}},
        ]
        return pipeline

    @classmethod
    def count_citations_by_author(cls, *, author_id: str) -> int:
        count_citations_pipeline = [
            {
                "$match": {
                    "authors.id": ObjectId(author_id),
                },
            },
            {"$unwind": "$citations_count"},
            {
                "$group": {
                    "_id": "$citations_count.source",
                    "count": {"$sum": "$citations_count.count"},
                },
            },
            {
                "$group": {
                    "_id": None,
                    "counts": {
                        "$push": {
                            "source": "$_id",
                            "count": "$count",
                        },
                    },
                },
            },
            {"$project": {"_id": 0, "counts": 1}},
        ]
        citations_count = next(
            engine.get_collection(Work).aggregate(count_citations_pipeline),
            {"counts": []},
        ).get("counts")
        return citations_count

    @classmethod
    def count_papers_by_author(
        cls, *, author_id: str, filters: dict[str, Any] = {}
    ) -> int:
        count_papers_pipeline = [
            {"$match": {"authors.id": ObjectId(author_id)}},
            {"$count": "total"},
        ]
        count_papers_pipeline += cls.get_filters(filters)
        papers_count = next(
            engine.get_collection(Work).aggregate(count_papers_pipeline),
            {"total": 0},
        ).get("total", 0)
        return papers_count

    @classmethod
    def count_papers(
        cls,
        *,
        affiliation_id: str,
        affiliation_type: str,
        filters: dict[str, Any] = {},
    ) -> int:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        count_papers_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        collection = Person if affiliation_type not in ["institution", "group"] else Work
        count_papers_pipeline += (
            [{"$replaceRoot": {"newRoot": "$works"}}] if collection != Work else []
        )
        count_papers_pipeline += cls.get_filters(filters)
        count_papers_pipeline.append({"$count": "total"})

        papers_count = next(
            engine.get_collection(collection).aggregate(count_papers_pipeline),
            {"total": 0},
        ).get("total", 0)
        return papers_count

    @classmethod
    def count_citations(
        cls, *, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, str | int]]:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        count_citations_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        count_citations_pipeline += [
            {
                "$project": {
                    "citations_count": f"${'works.' if affiliation_type not in ['institution', 'group'] else ''}citations_count"
                }
            },
            {"$unwind": "$citations_count"},
            {
                "$group": {
                    "_id": "$citations_count.source",
                    "count": {"$sum": "$citations_count.count"},
                }
            },
            {"$project": {"_id": 0, "source": "$_id", "count": 1}},
            {
                "$group": {
                    "_id": None,
                    "counts": {"$push": {"source": "$source", "count": "$count"}},
                }
            },
            {"$project": {"_id": 0, "counts": 1}},
        ]
        collection = Person if affiliation_type != "institution" else Work
        citations_count = next(
            engine.get_collection(collection).aggregate(count_citations_pipeline),
            {"counts": []},
        ).get("counts", [])
        return citations_count

    @staticmethod
    def get_sort_direction(sort: str | None = None) -> list[dict]:
        if not sort:
            return []
        sort_field, direction = (sort[:-1], -1) if sort.endswith("-") else (sort, 1)
        sort_traduction: dict[str, str] = {
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
                        }
                    }
                },
                {"$sort": {"source_priority": 1, "titles.0.title": direction}},
            ]
        else:
            pipeline += [
                {
                    "$sort": {
                        sort_traduction.get(sort_field, "titles.0.title"): direction
                    }
                }
            ]
        return pipeline

    @classmethod
    def filter_translation(cls, v: Any) -> dict[str, Any]:
        return {
            "type": {"$match": {"types.type": v}},
            "start_year": {"$match": {"year_published": {"$gte": v}}},
            "end_year": {"$match": {"year_published": {"$lte": v}}},
        }

    @classmethod
    def get_filters(cls, filters: dict[str, Any]) -> list[dict[str, Any]]:
        f_list = []
        for k, v in filters.items():
            f_list += [cls.filter_translation(v)[k]] if v else []
        return f_list

    @classmethod
    def __products_by_affiliation(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
        match: dict[str, Any] = {},
        filters: dict[str, str] = {},
        available_filters: bool = True,
        project: list[str] = [],
    ) -> tuple[Iterable[dict[str, Any]], dict[str, Any]]:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        works_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        collection = (
            Person if affiliation_type not in ["institution", "group"] else Work
        )
        works_pipeline += (
            [{"$replaceRoot": {"newRoot": "$works"}}] if collection != Work else []
        )
        # filtering
        works_pipeline += cls.get_filters(filters)
        available_filters = (
            cls.get_available_filters(pipeline=works_pipeline, collection=collection)
            if available_filters
            else {}
        )
        # sort
        works_pipeline += cls.get_sort_direction(sort)
        # navigation
        if match:
            works_pipeline += [{"$match": match}]
        works_pipeline += (
            [{"$project": {"_id": 1, **{p: 1 for p in project}}}] if project else []
        )
        works_pipeline += [{"$skip": skip}] if skip else []
        works_pipeline += [{"$limit": limit}] if limit else []
        results = engine.get_collection(collection).aggregate(works_pipeline)
        return results, available_filters

    @classmethod
    def get_research_products_by_affiliation(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
        filters: dict | None = {},
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        results, available_filters = cls.__products_by_affiliation(
            affiliation_id,
            affiliation_type,
            sort=sort,
            skip=skip,
            limit=limit,
            filters=filters,
        )
        return [
            {
                **WorkListApp.model_validate_json(
                    Work(**result).model_dump_json()
                ).model_dump(exclude={"id"}),
                "id": str(result["_id"]),
            }
            for result in results
        ], available_filters

    @classmethod
    def get_sources_by_affiliation(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        match: dict[str, Any] = {},
        project: list[str] = [],
    ) -> SourceIterator:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        works_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        collection = Person if affiliation_type not in ["institution", "group"] else Work
        works_pipeline += [
            {
                "$lookup": {
                    "from": "sources",
                    "localField": (
                        "works.source.id" if collection == Person else "source.id"
                    ),
                    "foreignField": "_id",
                    "as": "source",
                }
            },
            {"$unwind": "$source"},
            {
                "$addFields": {
                    "source.apc.year_published": (
                        "$works.year_published"
                        if collection == Person
                        else "year_published"
                    ),
                    "source.date_published": (
                        "$works.date_published"
                        if collection == Person
                        else "date_published"
                    ),
                }
            },
            {"$replaceRoot": {"newRoot": "$source"}},
            {"$match": match},
            {"$project": {"_id": 1, **{p: 1 for p in project}}},
        ]
        results = engine.get_collection(collection).aggregate(works_pipeline)
        return SourceIterator(results)

    @classmethod
    def get_research_products_by_affiliation_iterator(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
        match: dict | None = {},
        filters: dict | None = {},
        available_filters: bool = True,
        project: list[str] = [],
    ) -> tuple[Iterable[Work], dict[str, Any]]:
        results, available_filters = cls.__products_by_affiliation(
            affiliation_id,
            affiliation_type,
            sort=sort,
            skip=skip,
            limit=limit,
            match=match,
            filters=filters,
            available_filters=available_filters,
            project=project,
        )
        return WorkIterator(results), available_filters

    @classmethod
    def get_research_products_by_affiliation_csv(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Iterable[Work]:
        works, f = cls.__products_by_affiliation(
            affiliation_id,
            affiliation_type,
            sort=sort,
            skip=skip,
            limit=limit,
            available_filters=False
        )
        return WorkIterator(works)

    @classmethod
    def __products_by_author(
        cls,
        *,
        author_id: str,
        skip: int | None = None,
        limit: int | None = None,
        sort: str = "alphabetical",
        filters: dict | None = {},
    ) -> tuple[Iterable[dict[str, Any]], dict[str, str]]:
        works_pipeline = [
            {"$match": {"authors.id": ObjectId(author_id)}},
        ]
        works_pipeline += cls.get_filters(filters)
        available_filters = cls.get_available_filters(
            pipeline=works_pipeline, collection=Work
        )
        works_pipeline += cls.get_sort_direction(sort)
        works_pipeline += [{"$skip": skip}] if skip else []
        works_pipeline += [{"$limit": limit}] if limit else []
        return engine.get_collection(Work).aggregate(works_pipeline), available_filters

    @classmethod
    def get_research_products_by_author(
        cls,
        *,
        author_id: str,
        skip: int | None = None,
        limit: int | None = None,
        sort: str = "alphabetical",
        filters: dict | None = {},
    ) -> tuple[list[dict[str, Any]], dict[str, str]]:
        results, available_filters = cls.__products_by_author(
            author_id=author_id, skip=skip, limit=limit, sort=sort, filters=filters
        )
        return [
            {
                **WorkListApp.model_validate_json(
                    Work(**result).model_dump_json()
                ).model_dump(exclude={"id"}),
                "id": str(result["_id"]),
            }
            for result in results
        ], available_filters

    @classmethod
    def get_research_products_by_author_csv(
        cls,
        *,
        author_id: str,
        sort: str = "title",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        works, f = cls.__products_by_author(
            author_id=author_id, sort=sort, skip=skip, limit=limit
        )
        return [
            {
                **WorkCsv.model_validate_json(
                    Work(**result).model_dump_json()
                ).model_dump(exclude={"titles", "id"}),
                "id": str(result["_id"]),
            }
            for result in works
        ]

    @classmethod
    def get_available_filters(
        cls, *, pipeline: list[dict[str, Any]], collection: Any
    ) -> dict[str, Any]:
        filters = {}
        # type filter
        pipeline = pipeline.copy()
        pipeline += [{"$unwind": "$types"}, {"$group": {"_id": "$types.type"}}]
        types = list(
            map(
                lambda x: {
                    "label": settings.TYPES.get(x["_id"], x["_id"]),
                    "value": x["_id"],
                },
                engine.get_collection(collection).aggregate(pipeline),
            )
        )
        filters["type"] = types
        return filters


work_repository = WorkRepository(Work, WorkIterator)

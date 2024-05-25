from typing import Any, Iterable

from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine
from infraestructure.mongo.utils.iterators import work_iterator
from schemas.work import WorkCsv, WorkListApp
from core.config import settings


class WorkRepository(RepositoryBase):
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
            {"$unwind": "$works"},
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
        collection = Person if affiliation_type != "institution" else Work
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
                    "citations_count": f"${'works.' if affiliation_type!='institution' else ''}citations_count"
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
    def get_sort_direction(sort: str = "title") -> list[dict]:
        sort_field, direction = (sort[:-1], -1) if sort.endswith("-") else (sort, 1)
        sort_traduction: dict[str, str] = {
            "citations": "citations_count.count",
            "year": "year_published",
            "title": "titles.0.title",
            "alphabetical": "titles.0.title",
        }
        title_hierarchy = {
            "OpenAlex": 1,
            "Scholar": 2,
            "Scienti": 3,
            "Minciencias": 4,
            "Ranking": 5,
        }
        pipeline = []
        if sort_field == "year":
            pipeline += [{"$match": {"year_published": {"$ne": None}}}]
        if sort_field in ["title", "alphabetical"]:
            pipeline += [
                {
                    "$addFields": {
                        "title_hierarchy": {
                            "$indexOfArray": [
                                list(title_hierarchy.keys()),
                                "$titles.0.source",
                            ]
                        }
                    }
                },
                {"$sort": {"title_hierarchy": direction}},
            ]
        else:
            pipeline += [
                {"$sort": {sort_traduction.get(sort_field, "titles.0.title"): direction}}
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
        sort: str = "title",
        skip: int | None = None,
        limit: int | None = None,
        match: dict[str, Any] = {},
        filters: dict[str, str] = {},
    ) -> tuple[Iterable[dict[str, Any]], dict[str, Any]]:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        works_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        collection = Person if affiliation_type != "institution" else Work
        works_pipeline += (
            [{"$replaceRoot": {"newRoot": "$works"}}] if collection != Work else []
        )
        # filtering
        works_pipeline += cls.get_filters(filters)
        available_filters = cls.get_available_filters(
            pipeline=works_pipeline, collection=collection
        )
        # sort
        works_pipeline += cls.get_sort_direction(sort)
        # navigation
        if match:
            works_pipeline += [{"$match": match}]
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
        sort: str = "title",
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
    def get_research_products_by_affiliation_iterator(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str = "title",
        skip: int | None = None,
        limit: int | None = None,
        match: dict | None = {},
        filters: dict | None = {},
    ) -> tuple[Iterable[Work], dict[str, Any]]:
        results, available_filters = cls.__products_by_affiliation(
            affiliation_id,
            affiliation_type,
            sort=sort,
            skip=skip,
            limit=limit,
            match=match,
            filters=filters,
        )
        return work_iterator.set_cursor(results), available_filters

    @classmethod
    def get_research_products_by_affiliation_csv(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        sort: str = "title",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        works, f = cls.__products_by_affiliation(
            affiliation_id,
            affiliation_type,
            sort=sort,
            skip=skip,
            limit=limit,
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


work_repository = WorkRepository(Work)

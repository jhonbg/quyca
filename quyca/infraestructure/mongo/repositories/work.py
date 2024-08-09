from typing import Any, Iterable

from bson import ObjectId
from pymongo.collation import Collation

from quyca.infraestructure.mongo.repositories.base import RepositoryBase
from quyca.infraestructure.mongo.repositories.affiliation import affiliation_repository
from quyca.infraestructure.mongo.repositories.affiliation_calculations import (
    affiliation_calculations_repository,
)
from quyca.infraestructure.mongo.models import Work, Affiliation, general
from quyca.infraestructure.mongo.utils.session import engine
from quyca.infraestructure.mongo.utils.iterators import WorkIterator, SourceIterator
from quyca.core.config import settings


class WorkRepository(RepositoryBase[Work, WorkIterator]):
    def get_authors(self, *, id: str) -> Iterable[str]:
            """
            Retrieve the authors of a work based on its ID.

            Returns:
                A list of dictionaries representing the authors of the work.
            """
            with self.engine.session() as session:
                work = session.find_one(self.model, self.model.id == ObjectId(id))
                authors = work.authors
            return map(lambda x: x.model_dump_json(), authors)
    
    @classmethod
    def get_pipeline_works_by_affiliation_id(
        cls, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, Any]]:
        if affiliation_type in settings.institutions:
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
    def count_citations_by_author(cls, *, author_id: str) -> int:
        """
        Count the citations for a given author.

        Args:
            author_id (str): The ID of the author.

        Returns:
            int: The count of citations for the author.

        """
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
        return sorted(citations_count, key=lambda x: x["count"], reverse=True)

    @classmethod
    def count_papers_by_author(
        cls, *, author_id: str, filters: dict[str, Any] = {}
    ) -> int:
        """
        Count the number of papers written by a specific author.

        Args:
            author_id (str): The ID of the author.
            filters (dict[str, Any], optional): Additional filters to apply. Defaults to {}.

        Returns:
            int: The total number of papers written by the author.
        """
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
        """
        Count the number of papers for a given affiliation.

        Args:
            affiliation_id (str): The ID of the affiliation.
            affiliation_type (str): The type of the affiliation.
            filters (dict[str, Any], optional): Additional filters to apply. Defaults to {}.

        Returns:
            int: The total number of papers for the given affiliation.

        """
        affiliation_type = (
            "institution"
            if affiliation_type in settings.institutions
            else affiliation_type
        )
        count_papers_pipeline = cls.get_pipeline_works_by_affiliation_id(affiliation_id, affiliation_type)
        collection = (
            Affiliation if affiliation_type not in ["institution", "group"] else Work
        )
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
        cls, *, affiliation_id: str, affiliation_type: str = None
    ) -> list[general.CitationsCount]:
        """
        
        """
        affiliation_calculations = affiliation_calculations_repository.get_by_id(
            id=affiliation_id
        )
        return affiliation_calculations.citations_count

    @staticmethod
    def get_sort_direction(sort: str | None = None) -> list[dict]:
        if not sort:
            return []
        sort_field, direction = (sort[:-1], -1) if sort.endswith("-") else (sort, 1)
        sort_traslation: dict[str, str] = {
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
                        sort_traslation.get(sort_field, "titles.0.title"): direction,
                        "_id": -1,
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
            "institution"
            if affiliation_type in settings.institutions
            else affiliation_type
        )
        works_pipeline = cls.get_pipeline_works_by_affiliation_id(affiliation_id, affiliation_type)
        collection = (
            Affiliation if affiliation_type not in ["institution", "group"] else Work
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
        results = engine.get_collection(collection).aggregate(
            works_pipeline, collation=Collation(locale="es")
        )
        return results, available_filters

    @classmethod
    def get_sources_by_author(
        cls,
        author_id: str,
        *,
        match: dict[str, Any] = {},
        project: list[str] = [],
    ) -> SourceIterator:
        works_pipeline = [
            {"$match": {"authors.id": ObjectId(author_id)}},
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
            {"$match": match},
            {"$project": {"_id": 1, **{p: 1 for p in project}}},
        ]
        results = engine.get_collection(Work).aggregate(works_pipeline)
        return SourceIterator(results)

    @classmethod
    def get_sources_by_related_affiliations(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        relation_type: str,
        *,
        match: dict[str, Any] = {},
        project: list[str] = [],
    ) -> SourceIterator:
        pipeline, collection = affiliation_repository.related_affiliations_by_type(
            affiliation_id, relation_type, affiliation_type
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

        sources = engine.get_collection(collection).aggregate(pipeline)
        return SourceIterator(sources)

    @classmethod
    def __get_sources_by_affiliation(
        cls, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, Any]]:
        affiliation_type = (
            "institution"
            if affiliation_type in settings.institutions
            else affiliation_type
        )
        works_pipeline = cls.get_pipeline_works_by_affiliation_id(affiliation_id, affiliation_type)
        person = True if affiliation_type not in ["institution", "group"] else False
        works_pipeline += [
            {
                "$lookup": {
                    "from": "sources",
                    "localField": ("works.source.id" if person else "source.id"),
                    "foreignField": "_id",
                    "as": "source",
                }
            },
            {"$unwind": "$source"},
            {
                "$addFields": {
                    "source.apc.year_published": (
                        "$works.year_published" if person else "$year_published"
                    ),
                    "source.date_published": (
                        "$works.date_published" if person else "$date_published"
                    ),
                }
            },
            {"$replaceRoot": {"newRoot": "$source"}},
        ]
        return works_pipeline

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
            "institution"
            if affiliation_type in settings.institutions
            else affiliation_type
        )
        collection = (
            Affiliation if affiliation_type not in ["institution", "group"] else Work
        )
        pipeline = cls.__get_sources_by_affiliation(affiliation_id, affiliation_type)

        if match:
            pipeline += [
                {"$match": match},
            ]

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

        results = engine.get_collection(collection).aggregate(pipeline)
        return SourceIterator(results)

    @classmethod
    def get_research_products_by_affiliation(
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
            available_filters=False,
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
        available_filters: bool = True,
        match: dict | None = {},
        project: list[str] = [],
    ) -> tuple[Iterable[dict[str, Any]], dict[str, str]]:
        works_pipeline = [
            {"$match": {"authors.id": ObjectId(author_id)}},
        ]
        works_pipeline += cls.get_filters(filters)
        available_filters = (
            cls.get_available_filters(pipeline=works_pipeline, collection=Work)
            if available_filters
            else {}
        )
        works_pipeline += cls.get_sort_direction(sort)
        works_pipeline += [{"$match": match}] if match else []
        works_pipeline += (
            [{"$project": {"_id": 1, **{p: 1 for p in project}}}] if project else []
        )
        works_pipeline += [{"$skip": skip}] if skip else []
        works_pipeline += [{"$limit": limit}] if limit else []
        return (
            engine.get_collection(Work).aggregate(
                works_pipeline, collation=Collation(locale="es")
            ),
            available_filters,
        )

    @classmethod
    def get_research_products_by_author(
        cls,
        *,
        author_id: str,
        skip: int | None = None,
        limit: int | None = None,
        sort: str = "alphabetical",
        filters: dict | None = {},
        available_filters: bool = False,
        project: list[str] = [],
        match: dict | None = {},
    ) -> tuple[Iterable[Work], dict[str, str]]:
        results, available_filters = cls.__products_by_author(
            author_id=author_id,
            skip=skip,
            limit=limit,
            sort=sort,
            filters=filters,
            project=project,
            match=match,
        )
        return WorkIterator(results), available_filters

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


work_repository = WorkRepository(Work, iterator=WorkIterator)

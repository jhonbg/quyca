from json import loads
from typing import Any

from odmantic.query import desc, asc
from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine


class WorkRepository(RepositoryBase):
    @classmethod
    def wrap_pipeline(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        start_year: int = None,
        end_year: int = None,
        sort: str = "citations",
    ) -> list[dict[str, Any]]:
        match_works = (
            {"works.year_published": {"$gte": start_year, "$lte": end_year}}
            if start_year and end_year
            else {}
        )
        sort_field, direction = cls.get_sort_direction(sort)
        if affiliation_type == "institution":
            pipeline = [
                {
                    "$match": {
                        "authors.affiliations.id": ObjectId(affiliation_id),
                    },
                },
                {"$sort": {sort_field: direction}},
            ]
            year_published_match = (
                [{"$match": {"year_published": {"$gte": start_year, "$lte": end_year}}}]
                if start_year and end_year
                else []
            )
            return pipeline + year_published_match
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
            {"$match": match_works},
            {"$group": {"_id": "$works._id", "works": {"$first": "$works"}}},
            {
                "$project": {
                    "works._id": 1,
                    "works.citations_count": 1,
                    "works.year_published": 1,
                    "works.titles": 1,
                    "works.source": 1,
                    "works.authors": 1,
                    "works.subjects": 1,
                    "works.bibliographic_info": 1,
                }
            },
            {"$sort": {sort_field: direction}},
        ]
        return pipeline

    @classmethod
    def count_papers(cls, *, affiliation_id: str, affiliation_type: str) -> int:
        affiliation_type = (
            "institution" if affiliation_type == "Education" else affiliation_type
        )
        count_papers_pipeline = cls.wrap_pipeline(affiliation_id, affiliation_type)
        count_papers_pipeline.append({"$count": "total"})
        collection = Person if affiliation_type != "institution" else Work
        papers_count = next(
            engine.get_collection(collection).aggregate(count_papers_pipeline),
            {"total", 0},
        ).get("total", 0)
        return papers_count

    @classmethod
    def count_citations(
        cls, *, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, str | int]]:
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
            engine.get_collection(collection).aggregate(count_citations_pipeline), {}
        ).get("counts", [])
        return citations_count

    def get_research_products_by_affiliation(
        self,
        affiliation_id: str,
        affiliation_type: str,
        *,
        start_year: int,
        end_year: int,
        skip: int = 0,
        limit: int = 10,
        sort: str = "citations",
    ):
        if affiliation_type == "institution":
            sort_expresion = (
                desc(getattr(self.model, sort[:-1]))
                if sort.endswith("-")
                else asc(getattr(self.model, sort))
            )
            search_dict = (
                {"year_published": {"$gte": start_year, "$lte": end_year}}
                if start_year and end_year
                else {}
            )
            search_dict.update(
                {
                    "authors.affiliations.id": ObjectId(affiliation_id),
                    "types.type": {"$nin": ["department", "faculty", "group"]},
                }
            )
            with engine.session() as session:
                results = session.find(
                    Work, *search_dict, skip=skip, limit=limit, sort=sort_expresion
                )

    def get_research_products(
        self,
        *,
        id: str,
        start_year: int,
        end_year: int,
        skip: int = 0,
        limit: int = 10,
        sort: str = "citations",
    ) -> list[dict[str, Any]]:
        sort_expresion = None
        if sort:
            sort_expresion = (
                desc(getattr(self.model, sort[:-1]))
                if sort.endswith("-")
                else asc(getattr(self.model, sort))
            )
        filter_criteria = (
            id in map(lambda x: x.id, Work.authors),
            start_year <= Work.year_published <= end_year,
        )
        with engine.session() as session:
            results = session.find(
                Work, *filter_criteria, skip=skip, limit=limit, sort=sort_expresion
            )
        return [loads(result.json()) for result in results]


work_repository = WorkRepository(Work)

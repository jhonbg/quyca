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
                        "authors.affiliations.id": ObjectId("65efffc746fdfdf449882feb"),
                    },
                },
                {"$sort": {sort_field: direction}}
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

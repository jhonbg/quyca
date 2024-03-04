from json import loads
from typing import Any

from odmantic.query import desc, asc

from infraestructure.mongo.repositories.base import RepositorieBase
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.utils.session import engine


class WorkRepository(RepositorieBase):
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

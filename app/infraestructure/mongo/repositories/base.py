from typing import Generic, TypeVar, Any
from json import loads

from odmantic import Model
from odmantic.query import desc, asc

from infraestructure.mongo.utils.session import engine

ModelType = TypeVar("ModelType", bound=Model)


class RepositorieBase(Generic[ModelType]):
    def __init__(self, model: ModelType):
        self.model = model

    def get_all(
        self, *, query: dict[str, Any], skip: int = 0, limit: int = 10, sort: str = None
    ) -> list[ModelType]:
        with engine.session() as session:
            results = session.find(
                self.model,
                **{getattr(self.model, k): v for k, v in query.items()},
                skip=skip,
                limit=limit,
                sort=getattr(self.model, sort, None),
            )
        return [loads(result.json()) for result in results]

    def get_by_id(self, *, id: str) -> ModelType | None:
        with engine.session() as session:
            results = session.find_one(self.model, self.model.id == id)
        return results

    def search(
        self,
        *,
        keywords: str = "",
        skip: int = 0,
        limit: int = 10,
        sort: str = None,
        search: dict[str, Any] = {}
    ) -> tuple[list[ModelType], int]:
        filter_criteria = search
        if keywords:
            filter_criteria["$text"] = {"$search": keywords}
        sort_expresion = None
        if sort:
            sort_expresion = (
                desc(getattr(self.model, sort[:-1]))
                if sort.endswith("-")
                else asc(getattr(self.model, sort))
            )
        with engine.session() as session:
            results = session.find(
                self.model,
                filter_criteria,
                skip=skip,
                limit=limit,
                sort=sort_expresion,
            )
            count = session.count(self.model, filter_criteria)
        return [loads(result.json()) for result in results], count

    def count(self) -> int:
        with engine.session() as session:
            return session.count(self.model)

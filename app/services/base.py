from typing import Generic, TypeVar, Any, Type
from json import loads

from odmantic import Model

from infraestructure.mongo.repositories.base import RepositorieBase
from schemas.general import QueryBase, GeneralMultiResponse


ModelType = TypeVar("ModelType", bound=Model)
RepositorieType = TypeVar("RepositorieType", bound=RepositorieBase)
ParamsType = TypeVar("ParamsType", bound=QueryBase)


class ServiceBase(Generic[ModelType, RepositorieType, ParamsType]):
    def __init__(self, repository: RepositorieType):
        self.repository = repository

    def get_all(self, *, params: ParamsType) -> dict[str, Any]:
        db_objs = self.repository.get_all(
            query={}, skip=params.skip, limit=params.limit, sort=params.sort
        )
        total_results = self.repository.count()
        results = GeneralMultiResponse(total_results=total_results)
        results.data = db_objs
        return loads(results.json())

    def get_by_id(self, *, id: str) -> dict[str, Any]:
        db_obj = self.repository.get_by_id(id=id)
        return loads(db_obj.json())

    def search(self, *, params: ParamsType):
        db_objs, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.limit,
            sort=params.sort,
        )
        results = GeneralMultiResponse(total_results=count)
        results.data = db_objs
        return loads(results.json())

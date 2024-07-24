from typing import Protocol, TypeVar, Any, Literal, Iterable

from protocols.mongo.utils.iterators import CollectionIterator

ModelType = TypeVar("ModelType")
IteratorType = TypeVar("IteratorType", bound=CollectionIterator)


class RepositoryBase(Protocol[ModelType, IteratorType]):
    def __init__(
        self,
        model: type[ModelType],
        iterator: type[IteratorType] = None,
        engine: Any = None,
    ):
        ...

    def get_all(
        self, *, query: dict[str, Any], skip: int = 0, limit: int = 10, sort: str = None
    ) -> list[ModelType]:
        ...

    def get_by_id(self, *, id: str) -> str | None:
        ...

    def search(
        self,
        *,
        keywords: str = "",
        skip: int = 0,
        limit: int = 10,
        sort: str = "",
        search: dict[str, Any] = {}
    ) -> tuple[Iterable[ModelType], int]:
        ...

    def count(self) -> int:
        ...

    @staticmethod
    def get_sort_direction(sort: str) -> tuple[str, Literal[1, -1]]:
        ...

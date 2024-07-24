from typing import Any, Iterable

from protocols.mongo.repositories.base import RepositoryBase
from protocols.mongo.models import Work, general
from protocols.mongo.utils.iterators import WorkIterator, SourceIterator


class WorkRepository(RepositoryBase[Work, WorkIterator]):
    @classmethod
    def wrap_pipeline(
        cls, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, Any]]:
        ...

    @classmethod
    def count_citations_by_author(cls, *, author_id: str) -> int:
        ...

    @classmethod
    def count_papers_by_author(
        cls, *, author_id: str, filters: dict[str, Any] = {}
    ) -> int:
        ...

    @classmethod
    def count_papers(
        cls,
        *,
        affiliation_id: str,
        affiliation_type: str,
        filters: dict[str, Any] = {},
    ) -> int:
        ...

    @classmethod
    def count_citations(
        cls, *, affiliation_id: str, affiliation_type: str = None
    ) -> list[general.CitationsCount]:
        ...

    @staticmethod
    def get_sort_direction(sort: str | None = None) -> list[dict]:
        ...

    @classmethod
    def filter_translation(cls, v: Any) -> dict[str, Any]:
        ...

    @classmethod
    def get_filters(cls, filters: dict[str, Any]) -> list[dict[str, Any]]:
        ...

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
        ...

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
        ...

    @classmethod
    def get_sources_by_author(
        cls,
        author_id: str,
        *,
        match: dict[str, Any] = {},
        project: list[str] = [],
    ) -> SourceIterator:
        ...

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
        ...

    @classmethod
    def __get_sources_by_affiliation(
        cls, affiliation_id: str, affiliation_type: str
    ) -> list[dict[str, Any]]:
        ...

    @classmethod
    def get_sources_by_affiliation(
        cls,
        affiliation_id: str,
        affiliation_type: str,
        *,
        match: dict[str, Any] = {},
        project: list[str] = [],
    ) -> SourceIterator:
        ...

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
        ...

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
        ...

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
        ...

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
        ...

    @classmethod
    def get_research_products_by_author_iterator(
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
        ...

    @classmethod
    def get_research_products_by_author_csv(
        cls,
        *,
        author_id: str,
        sort: str = "title",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        ...

    @classmethod
    def get_available_filters(
        cls, *, pipeline: list[dict[str, Any]], collection: Any
    ) -> dict[str, Any]:
        ...
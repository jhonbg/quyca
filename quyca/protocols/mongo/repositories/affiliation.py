from typing import Any, Iterable, TypeVar

from protocols.mongo.repositories.base import RepositoryBase
from protocols.mongo.models.affiliation import Affiliation
from protocols.mongo.models.person import Person
from protocols.mongo.utils.iterators import AffiliationIterator
from schemas.affiliation import AffiliationRelated


Model = TypeVar("Model", bound=Any)


class AffiliationRepository(RepositoryBase[Affiliation, AffiliationIterator]):
    def __groups_by_affiliation(
        self, idx: str, typ: str
    ) -> tuple[list[dict[str, Any]], Model]:
        ...

    def related_affiliations_by_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> tuple[list[dict[str, Any]], Model]:
        ...

    def get_affiliations_related_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> Iterable[AffiliationRelated]:
        ...

    def get_groups_by_affiliation(self, idx: str, typ: str) -> Iterable[Affiliation]:
        ...

    def get_authors_by_affiliation(self, idx: str, typ: str) -> list[Person]:
        ...

    @classmethod
    def upside_relations(
        cls, relations: list[dict, str], typ: str
    ) -> tuple[list[dict[str, Any]], str]:
        ...

    def get_products(
        self,
        *,
        affiliation_id: int,
        affiliation_type: str,
        skip: int = 0,
        limit: int = 100
    ): ...
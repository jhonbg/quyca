from typing import Protocol, TypeVar, Iterable, ClassVar

from quyca.protocols.mongo.models import (
    Affiliation,
    Person,
    Source,
    Work,
    AffiliationCalculations,
)

ModelType = TypeVar("ModelType")


class CollectionIterator(Protocol[ModelType]):
    collection: ClassVar[type[ModelType]]

    def __init__(self, cursor: Iterable[ModelType]):
        ...

    def __iter__(self):
        ...

    def __next__(self) -> ModelType:
        ...


class AffiliationIterator(CollectionIterator[Affiliation]):
    collection = Affiliation


class PersonIterator(CollectionIterator[Person]):
    collection = Person


class SourceIterator(CollectionIterator[Source]):
    collection = Source


class WorkIterator(CollectionIterator[Work]):
    collection = Work


class AffiliationCalculationsIterator(CollectionIterator[AffiliationCalculations]):
    collection = AffiliationCalculations

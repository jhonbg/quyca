from typing import Generic, TypeVar, Iterable, ClassVar

from odmantic import Model

from infraestructure.mongo.models import Affiliation, Person, Source, Work

ModelType = TypeVar("ModelType", bound=Model)


class CollectionIterator(Generic[ModelType]):
    collection: ClassVar[type[ModelType]]

    def __init__(self, cursor: Iterable[ModelType]):
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self) -> ModelType:
        try:
            doc = next(self.cursor)
        except StopIteration:
            raise
        else:
            doc["id"] = doc["_id"]
            obj = self.collection.model_validate(doc)
            return obj


class AffiliationIterator(CollectionIterator[Affiliation]):
    collection = Affiliation

class PersonIterator(CollectionIterator[Person]):
    collection = Person

class SourceIterator(CollectionIterator[Source]):
    collection = Source

class WorkIterator(CollectionIterator[Work]):
    collection = Work

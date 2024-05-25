from typing import Generic, TypeVar, Iterable, Any

from odmantic import Model

from infraestructure.mongo.models import Affiliation, Person, Source, Work

ModelType = TypeVar("ModelType", bound=Model)


class CollectionIterator(Generic[ModelType]):
    def __init__(self, collection: ModelType):
        self.collection = collection

    def set_cursor(self, cursor: Iterable[dict[str, Any]]):
        self.cursor = cursor
        return self

    def __iter__(self):
        return self

    def __next__(self) -> ModelType:
        try:
            doc = next(self.cursor)
        except StopIteration:
            raise
        else:
            obj = self.collection.model_validate(doc)
            return obj


affiliation_iterator = CollectionIterator(Affiliation)
person_iterator = CollectionIterator(Person)
source_iterator = CollectionIterator(Source)
work_iterator = CollectionIterator(Work)

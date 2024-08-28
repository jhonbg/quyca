from protocols.mongo.models.person import Person
from protocols.mongo.repositories.base import RepositoryBase
from protocols.mongo.utils.iterators import PersonIterator


class PersonRepository(RepositoryBase[Person, PersonIterator]):
    ...

from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.utils.iterators import PersonIterator


class PersonRepository(RepositoryBase[Person, PersonIterator]):
    ...

person_repository = PersonRepository(Person, iterator=PersonIterator)
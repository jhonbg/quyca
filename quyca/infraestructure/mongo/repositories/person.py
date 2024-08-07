from quyca.infraestructure.mongo.models.person import Person
from quyca.infraestructure.mongo.repositories.base import RepositoryBase
from quyca.infraestructure.mongo.utils.iterators import PersonIterator


class PersonRepository(RepositoryBase[Person, PersonIterator]):
    ...

person_repository = PersonRepository(Person, iterator=PersonIterator)
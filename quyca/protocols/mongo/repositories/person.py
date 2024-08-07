from quyca.protocols.mongo.models.person import Person
from quyca.protocols.mongo.repositories.base import RepositoryBase
from quyca.protocols.mongo.utils.iterators import PersonIterator


class PersonRepository(RepositoryBase[Person, PersonIterator]):
    ...
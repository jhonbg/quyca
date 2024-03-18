from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.base import RepositoryBase


class PersonRepository(RepositoryBase[Person]):
    ...

person_repository = PersonRepository(Person)
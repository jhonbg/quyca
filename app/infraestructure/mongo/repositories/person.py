from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.base import RepositorieBase


class PersonRepository(RepositorieBase[Person]):
    ...

person_repository = PersonRepository(Person)
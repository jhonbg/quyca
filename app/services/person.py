from services.base import ServiceBase
from schemas.person import PersonQueryParams
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.person import (
    PersonRepository,
    person_repository,
)


class PersonService(ServiceBase[Person, PersonRepository, PersonQueryParams]):
    ...


person_service = PersonService(person_repository)

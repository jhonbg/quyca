from typing import Type, Any
from json import loads

from schemas.general import GeneralMultiResponse
from services.base import ServiceBase
from services.affiliation import affiliation_service
from schemas.person import PersonQueryParams, PersonSearch, PersonInfo
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.person import (
    PersonRepository,
    person_repository,
)
from infraestructure.mongo.repositories.work import WorkRepository
from core.config import settings


class PersonService(
    ServiceBase[Person, PersonRepository, PersonQueryParams, PersonSearch, PersonInfo]
):
    def get_info(self, *, id: str) -> dict[str, Any]:
        basic_info = self.repository.get_by_id(id=id)
        person = self.info_class.model_validate_json(basic_info)
        self.update_author_search(person)
        # get high affiliation on hierarchy
        institution = next(
            filter(
                lambda x: x.types[0].type in settings.institutions, person.affiliations
            ),
            None,
        )
        if institution:
            person.logo = affiliation_service.get_by_id(id=institution.id).logo
        return {"data": person.model_dump(by_alias=True), "filters": {}}

    def update_author_search(self, author: PersonSearch) -> PersonSearch:
        author.citations_count = WorkRepository.count_citations_by_author(
            author_id=author.id
        )
        author.products_count = WorkRepository.count_papers_by_author(
            author_id=author.id
        )
        return author

    def update_search(
        self, response: GeneralMultiResponse[type[PersonSearch]]
    ) -> GeneralMultiResponse[type[PersonSearch]]:
        response.data = [
            self.update_author_search(PersonSearch(**obj)) for obj in response.data
        ]

    def search(
        self, *, params: PersonQueryParams
    ) -> GeneralMultiResponse[type[PersonSearch]]:
        db_objs, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            search=params.get_search,
        )
        results = GeneralMultiResponse[type[PersonSearch]](
            total_results=count, page=params.page
        )
        data = [
            self.search_class.model_validate_json(obj.model_dump_json())
            for obj in db_objs
        ]
        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True, by_alias=True))


person_service = PersonService(person_repository, PersonSearch, PersonInfo)

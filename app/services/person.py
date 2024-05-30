from typing import Type
from json import loads

from schemas.general import GeneralMultiResponse
from services.base import ServiceBase
from schemas.person import PersonQueryParams, PersonSearch
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.repositories.person import (
    PersonRepository,
    person_repository,
)
from infraestructure.mongo.repositories.work import WorkRepository


class PersonService(
    ServiceBase[Person, PersonRepository, PersonQueryParams, PersonSearch, PersonSearch]
):
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


person_service = PersonService(person_repository, PersonSearch, PersonSearch)

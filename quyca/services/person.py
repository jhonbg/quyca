from typing import Any, Callable
from json import loads

from quyca.schemas.general import GeneralMultiResponse
from quyca.schemas.affiliation import AffiliationInfo
from quyca.services.base import ServiceBase
from quyca.services.plots.person import person_plots_service
from quyca.schemas.person import PersonQueryParams, PersonSearch, PersonInfo
from quyca.protocols.mongo.models.person import Person
from quyca.protocols.mongo.repositories.person import PersonRepository
from quyca.protocols.mongo.repositories.work import WorkRepository
from quyca.protocols.mongo.repositories.affiliation import AffiliationRepository
from quyca.core.config import settings


class PersonService(
    ServiceBase[Person, PersonRepository, PersonQueryParams, PersonSearch, PersonInfo]
):
    def register_works_repository(self, *, repository: WorkRepository):
        self.work_repository = repository

    def register_affiliation_repository(self, *, repository: AffiliationRepository):
        self.affiliation_repository = repository

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
            person.logo = AffiliationInfo.model_validate_json(
                self.affiliation_repository.get_by_id(id=institution.id)
            ).logo
        return {"data": person.model_dump(by_alias=True), "filters": {}}

    def update_author_search(self, author: PersonSearch) -> PersonSearch:
        author.citations_count = self.work_repository.count_citations_by_author(
            author_id=author.id
        )
        author.products_count = self.work_repository.count_papers_by_author(
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
            self.update_author_search(
                self.search_class.model_validate_json(obj.model_dump_json())
            )
            for obj in db_objs
        ]
        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True, by_alias=True))

    @property
    def plot_mappings(self) -> dict[str, Callable[[Any, Any], dict[str, list] | None]]:
        return {
            "year_type": person_plots_service.get_products_by_year_by_type,
            "year_citations": person_plots_service.get_citations_by_year,
            "year_apc": person_plots_service.get_apc_by_year,
            "year_oa": person_plots_service.get_oa_by_year,
            "year_publisher": person_plots_service.get_products_by_year_by_publisher,
            "year_h": person_plots_service.get_h_by_year,
            "year_researcher": person_plots_service.get_products_by_year_by_researcher_category,
            "title_words": person_plots_service.get_title_words,
            "products_publisher": person_plots_service.get_products_by_publisher,
            "products_subject": person_plots_service.get_products_by_subject,
            "products_database": person_plots_service.get_products_by_database,
            "products_oa": person_plots_service.get_products_by_open_access_status,
            "products_age": person_plots_service.get_products_by_author_age,
            "scienti_rank": person_plots_service.get_products_by_scienti_rank,
            "scimago_rank": person_plots_service.get_products_by_scimago_rank,
            "published_institution": person_plots_service.get_publisher_same_institution,
            "collaboration_worldmap": person_plots_service.get_coauthorships_worldmap,
            "collaboration_colombiamap": person_plots_service.get_coauthorships_colombiamap,
            "collaboration_network": person_plots_service.get_coauthorships_network,
        }


person_service = PersonService(PersonSearch, PersonInfo)

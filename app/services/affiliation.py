from json import loads

from schemas.general import GeneralMultiResponse
from services.base import ServiceBase
from schemas.affiliation import (
    AffiliationQueryParams,
    AffiliationSearch,
    Affiliation as AffiliationSchema,
)
from infraestructure.mongo.models.affiliation import Affiliation
from infraestructure.mongo.repositories.affiliation import (
    AffiliationRepository,
    affiliation_repository,
)
from infraestructure.mongo.repositories.work import WorkRepository


class AffiliationService(
    ServiceBase[
        Affiliation,
        AffiliationRepository,
        AffiliationQueryParams,
        AffiliationSearch,
        AffiliationSchema,
    ]
):
    def update_affiliation_search(self, obj: AffiliationSearch) -> AffiliationSearch:
        obj.affiliations = self.repository.upside_relations(
            [rel.model_dump() for rel in obj.relations], obj.types[0].type
        )
        obj.products_count = WorkRepository.count_papers(
            affiliation_id=obj.id, affiliation_type=obj.types[0].type
        )
        obj.citations_count = WorkRepository.count_citations(
            affiliation_id=obj.id, affiliation_type=obj.types[0].type
        )
        return obj

    def search(
        self, *, params: AffiliationQueryParams
    ) -> GeneralMultiResponse[type[AffiliationSearch]]:
        db_objs, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            search=params.get_search,
        )
        results = GeneralMultiResponse[type[AffiliationSearch]](
            total_results=count, page=params.page
        )
        data = [
            self.update_affiliation_search(
                AffiliationSearch.model_validate_json(obj.model_dump_json())
            )
            for obj in db_objs
        ]

        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True, by_alias=True))


affiliation_service = AffiliationService(
    affiliation_repository, AffiliationSearch, AffiliationSchema
)

from json import loads
from typing import Any, Callable

from schemas.general import GeneralMultiResponse
from schemas.affiliation import (
    AffiliationQueryParams,
    AffiliationSearch,
    Affiliation as AffiliationSchema,
    AffiliationInfo,
    AffiliationRelatedInfo,
)
from services.base import ServiceBase
from services.plots.affiliation import affiliation_plots_service
from protocols.mongo.models.affiliation import Affiliation
from protocols.mongo.repositories.affiliation import (
    AffiliationRepository,
)
from protocols.mongo.repositories.affiliation_calculations import (
    AffiliationCalculationsRepository,
)
from protocols.mongo.repositories.work import WorkRepository
from core.logging import get_logger

log = get_logger(__name__)


class AffiliationService(
    ServiceBase[
        Affiliation,
        AffiliationRepository,
        AffiliationQueryParams,
        AffiliationSearch,
        AffiliationInfo,
    ]
):
    def register_calculations_repository(
        self, *, repository: AffiliationCalculationsRepository
    ):
        log.info("Registering affiliation calculations repository")
        self.affiliation_calculations_repository = repository

    def get_info(self, *, id: str) -> dict[str, Any]:
        basic_info = self.repository.get_by_id(id=id)
        affiliation = self.info_class.model_validate_json(basic_info)
        self.update_affiliation_search(affiliation)
        return {"data": affiliation.model_dump(by_alias=True), "filters": {}}

    def update_affiliation_search(self, obj: AffiliationSearch) -> AffiliationSearch:
        affiliations, logo = self.repository.upside_relations(
            [rel.model_dump() for rel in obj.relations], obj.types[0].type
        )
        obj.affiliations = affiliations
        obj.logo = logo if logo else obj.logo
        obj.products_count = WorkRepository.count_papers(
            affiliation_id=obj.id, affiliation_type=obj.types[0].type
        )
        obj.citations_count = self.affiliation_calculations_repository.get_by_id(
            id=obj.id
        ).citations_count
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

    def get_affiliations(self, *, id: str, typ: str = None) -> dict[str, list[Any]]:
        data = {}
        if typ == "institution":
            data["faculties"] = self.repository.get_affiliations_related_type(
                id, "faculty", typ
            )
        if typ in ["faculty", "institution"]:
            data["departments"] = self.repository.get_affiliations_related_type(
                id, "department", typ
            )
        if typ in ["department", "faculty", "institution"]:
            data["groups"] = self.repository.get_affiliations_related_type(
                id, "group", typ
            )
        if typ in ["group", "department", "faculty"]:
            data["authors"] = self.repository.get_authors_by_affiliation(id, typ)

        result = AffiliationRelatedInfo.model_validate(data, from_attributes=True)

        return result.model_dump(exclude_none=True)

    @property
    def plot_mappings(self) -> dict[str, Callable[[Any, Any], dict[str, list] | None]]:
        return {
            "year_type": affiliation_plots_service.get_products_by_year_by_type,
            "type,faculty": affiliation_plots_service.get_products_by_affiliation_by_type,
            "type,department": affiliation_plots_service.get_products_by_affiliation_by_type,
            "type,group": affiliation_plots_service.get_products_by_affiliation_by_type,
            "year_citations": affiliation_plots_service.get_citations_by_year,
            "year_apc": affiliation_plots_service.get_apc_by_year,
            "year_oa": affiliation_plots_service.get_oa_by_year,
            "year_publisher": affiliation_plots_service.get_products_by_year_by_publisher,
            "year_h": affiliation_plots_service.get_h_by_year,
            "year_researcher": affiliation_plots_service.get_products_by_year_by_researcher_category,
            "year_group": affiliation_plots_service.get_products_by_year_by_group_category,
            "title_words": affiliation_plots_service.get_title_words,
            "citations,faculty": affiliation_plots_service.get_citations_by_affiliations,
            "citations,department": affiliation_plots_service.get_citations_by_affiliations,
            "citations,group": affiliation_plots_service.get_citations_by_affiliations,
            "products,faculty": affiliation_plots_service.get_products_by_affiliations,
            "products,department": affiliation_plots_service.get_products_by_affiliations,
            "products,group": affiliation_plots_service.get_products_by_affiliations,
            "apc,faculty": affiliation_plots_service.get_apc_by_affiliations,
            "apc,department": affiliation_plots_service.get_apc_by_affiliations,
            "apc,group": affiliation_plots_service.get_apc_by_affiliations,
            "h,faculty": affiliation_plots_service.get_h_by_affiliations,
            "h,department": affiliation_plots_service.get_h_by_affiliations,
            "h,group": affiliation_plots_service.get_h_by_affiliations,
            "products_publisher": affiliation_plots_service.get_products_by_publisher,
            "products_subject": affiliation_plots_service.get_products_by_subject,
            "products_database": affiliation_plots_service.get_products_by_database,
            "products_oa": affiliation_plots_service.get_products_by_open_access_status,
            "products_sex": affiliation_plots_service.get_products_by_author_sex,
            "products_age": affiliation_plots_service.get_products_by_author_age,
            "scienti_rank": affiliation_plots_service.get_products_by_scienti_rank,
            "scimago_rank": affiliation_plots_service.get_products_by_scimago_rank,
            "published_institution": affiliation_plots_service.get_publisher_same_institution,
            "collaboration_worldmap": affiliation_plots_service.get_coauthorships_worldmap,
            "collaboration_colombiamap": affiliation_plots_service.get_coauthorships_colombiamap,
            "collaboration_network": affiliation_plots_service.get_coauthorships_network,
        }


affiliation_service = AffiliationService(AffiliationSearch, AffiliationInfo)

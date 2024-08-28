from json import loads
from typing import Any, Callable

from schemas.general import GeneralMultiResponse
from schemas.affiliation import (
    AffiliationQueryParams,
    AffiliationSearch,
    AffiliationInfo,
    AffiliationRelatedInfo,
)
from schemas.work import (
    WorkProccessed,
    WorkListApp,
    WorkQueryParams,
    WorkCsv,
    Work as WorkSchema,
)
from schemas.person import PersonInfo
from services.base import ServiceBase
from services.source import source_service
from protocols.mongo.models.affiliation import Affiliation
from protocols.mongo.repositories.affiliation import (
    AffiliationRepository,
)
from protocols.mongo.repositories.affiliation_calculations import (
    AffiliationCalculationsRepository,
)
from protocols.mongo.repositories.person import PersonRepository
from protocols.mongo.repositories.work import WorkRepository
from core.logging import get_logger
from core.config import settings


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
    def register_works_repository(self, *, repository: WorkRepository):
        log.info("Registering work repository")
        self.work_repository = repository

    def register_calculations_repository(
        self, *, repository: AffiliationCalculationsRepository
    ):
        log.info("Registering affiliation calculations repository")
        self.affiliation_calculations_repository = repository

    def register_person_repository(self, *, repository: PersonRepository):
        log.info("Registering person repository")
        self.person_repository = repository

    def get_info(self, *, id: str) -> dict[str, Any]:
        basic_info = self.repository.get_by_id(id=id)
        affiliation = self.info_class.model_validate_json(basic_info)
        self.update_affiliation_search(affiliation)
        return {"data": affiliation.model_dump(by_alias=True), "filters": {}}

    def update_author_external_ids(self, work: WorkProccessed):
        for author in work.authors:
            ext_ids = (
                PersonInfo.model_validate_json(
                    self.person_repository.get_by_id(id=author.id)
                ).external_ids
                if author.id
                else []
            )
            author.external_ids = [ext_id.model_dump() for ext_id in ext_ids]
        return work

    def update_affiliation_search(self, obj: AffiliationSearch) -> AffiliationSearch:
        affiliations, logo = self.repository.upside_relations(
            [rel.model_dump() for rel in obj.relations], obj.types[0].type
        )
        obj.affiliations = affiliations
        obj.logo = logo if logo else obj.logo
        obj.products_count = self.work_repository.count_papers(
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

    def get_research_products_json(
        self, *, id: str, typ: str, params: AffiliationQueryParams
    ) -> dict[str, Any]:
        works = self.work_repository.get_research_products_by_affiliation_csv(
            affiliation_id=id,
            affiliation_type=typ,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
        )
        data = [
            source_service.update_source(
                WorkSchema.model_validate_json(work.model_dump_json())
            ).model_dump()
            for work in works
        ]
        count = self.work_repository.count_papers(
            affiliation_id=id, affiliation_type=typ
        )
        return {
            "data": data,
            "info": {
                "total_products": count,
                "count": len(data),
                "cursor": params.get_cursor(
                    path=f"{settings.API_URL_PREFIX}/affiliation/{typ}/{id}/research/products",
                    total=count,
                ),
            },
        }

    def get_research_products(
        self, *, id: str, typ: str, params: WorkQueryParams
    ) -> dict[str, Any]:
        (
            works,
            available_filters,
        ) = self.work_repository.get_research_products_by_affiliation(
            affiliation_id=id,
            affiliation_type=typ,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            filters=params.get_filter(),
        )
        total_works = self.work_repository.count_papers(
            affiliation_id=id, affiliation_type=typ, filters=params.get_filter()
        )
        data = [
            WorkListApp.model_validate_json(
                self.update_author_external_ids(work).model_dump_json()
            ).model_dump()
            for work in works
        ]
        return {
            "data": data,
            "total_results": total_works,
            "count": len(data),
            "filters": available_filters,
        }

    def get_research_products_csv(
        self,
        *,
        id: str,
        typ: str,
        sort: str = None,
        skip: int = None,
        limit: int = None,
    ) -> list[dict[str, Any]]:
        works = self.work_repository.get_research_products_by_affiliation_csv(
            affiliation_id=id, affiliation_type=typ, sort=sort, skip=skip, limit=limit
        )
        return [
            source_service.update_source(
                WorkCsv.model_validate_json(work.model_dump_json())
            ).model_dump()
            for work in works
        ]


affiliation_service = AffiliationService(AffiliationSearch, AffiliationInfo)

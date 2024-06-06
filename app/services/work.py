from typing import Any
from json import loads

from services.base import ServiceBase
from schemas.work import WorkQueryParams, WorkProccessed, WorkListApp, WorkCsv
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.repositories.work import (
    WorkRepository,
    work_repository,
)
from services.person import person_service
from services.source import source_service
from schemas.general import GeneralMultiResponse


class WorkService(
    ServiceBase[Work, WorkRepository, WorkQueryParams, WorkListApp, WorkProccessed]
):
    @staticmethod
    def update_authors_external_ids(work: WorkProccessed):
        for author in work.authors:
            author.external_ids = (
                person_service.get_by_id(id=author.id).external_ids if author.id else []
            )

    @staticmethod
    def update_source(work: WorkProccessed):
        if work.source.id:
            source = source_service.get_by_id(id=work.source.id)
            serials = {}
            for serial in source.external_ids:
                serials[serial.source] = serial.id
            work.source.serials = serials

    def count_papers(
        self,
        *,
        affiliation_id: str | None = None,
        affiliation_type: str | None = None,
        author_id: str | None = None,
    ) -> int:
        if affiliation_id and affiliation_type:
            return WorkRepository.count_papers(
                affiliation_id=affiliation_id, affiliation_type=affiliation_type
            )
        if author_id:
            return WorkRepository.count_papers_by_author(author_id=author_id)
        return 0

    def get_info(self, *, id: str) -> dict[str, Any]:
        work = super().get_by_id(id=id)
        self.update_authors_external_ids(work)
        self.update_source(work)
        return {"data": work.model_dump(exclude_none=True, exclude={"titles"})}

    def get_research_products_by_affiliation(
        self,
        *,
        affiliation_id: str,
        affiliation_type: str,
        skip: int | None = None,
        limit: int | None = None,
        sort: str | None = "title",
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        works, available_filters = (
            WorkRepository.get_research_products_by_affiliation_iterator(
                affiliation_id,
                affiliation_type,
                skip=skip,
                limit=limit,
                sort=sort,
                filters=filters,
            )
        )
        total_works = WorkRepository.count_papers(
            affiliation_id=affiliation_id,
            affiliation_type=affiliation_type,
            filters=filters,
        )
        data = [
            WorkListApp.model_validate_json(work.model_dump_json()).model_dump()
            for work in works
        ]
        return {
            "data": data,
            "total_results": total_works,
            "count": len(data),
            "filters": available_filters,
        }

    def get_research_products_info_by_affiliation_csv(
        self,
        *,
        affiliation_id: str,
        affiliation_type: str,
        start_year: int | None = None,
        end_year: int | None = None,
        skip: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
    ) -> list[dict[str, Any]]:
        works = WorkRepository.get_research_products_by_affiliation_csv(
            affiliation_id, affiliation_type, sort=sort, skip=skip, limit=limit
        )
        return [
            WorkCsv.model_validate_json(work.model_dump_json()).model_dump()
            for work in works
        ]

    def get_research_products_by_author(
        self,
        *,
        author_id: str,
        skip: int | None = None,
        limit: int | None = None,
        sort: str = "alphabetical",
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        works, available_filters = WorkRepository.get_research_products_by_author(
            author_id=author_id, skip=skip, limit=limit, sort=sort, filters=filters
        )
        total_works = WorkRepository.count_papers_by_author(
            author_id=author_id, filters=filters
        )
        return {
            "data": works,
            "total_results": total_works,
            "count": len(works),
            "filters": available_filters,
        }

    def get_research_products_by_author_csv(
        self,
        *,
        author_id: str,
        sort: str | None = "title",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return WorkRepository.get_research_products_by_author_csv(
            author_id=author_id, sort=sort, skip=skip, limit=limit
        )

    def search_api(self, *, params: WorkQueryParams) -> dict[str, Any]:
        works, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            search=params.get_search,
        )
        results = GeneralMultiResponse[WorkCsv](total_results=count, page=params.page)
        data = [WorkCsv.model_validate_json(work.model_dump_json()) for work in works]
        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True))


work_service = WorkService(work_repository, WorkListApp, WorkProccessed)

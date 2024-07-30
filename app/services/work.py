from typing import Any
from json import loads

from services.base import ServiceBase
from schemas.work import (
    WorkQueryParams,
    WorkProccessed,
    WorkListApp,
    WorkCsv,
    Work as WorkSchema,
)
from protocols.mongo.models.work import Work
from protocols.mongo.repositories.work import WorkRepository
from services.person import person_service
from services.source import source_service
from schemas.general import GeneralMultiResponse


class WorkService(
    ServiceBase[Work, WorkRepository, WorkQueryParams, WorkListApp, WorkProccessed]
):
    @staticmethod
    def update_authors_external_ids(work: WorkProccessed):
        for author in work.authors:
            ext_ids = (
                person_service.get_by_id(id=author.id).external_ids if author.id else []
            )
            author.external_ids = [ext_id.model_dump() for ext_id in ext_ids]
        return work

    
    def count_papers(
        self,
        *,
        affiliation_id: str | None = None,
        affiliation_type: str | None = None,
        author_id: str | None = None,
    ) -> int:
        if affiliation_id and affiliation_type:
            return self.repository.count_papers(
                affiliation_id=affiliation_id, affiliation_type=affiliation_type
            )
        if author_id:
            return self.repository.count_papers_by_author(author_id=author_id)
        return 0

    def get_info(self, *, id: str) -> dict[str, Any]:
        work = super().get_by_id(id=id)
        self.update_authors_external_ids(work)
        source_service.update_source(work)
        return {"data": work.model_dump(exclude_none=True, exclude={"titles"})}

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
        works = self.repository.get_research_products_by_affiliation_csv(
            affiliation_id, affiliation_type, sort=sort, skip=skip, limit=limit
        )
        return [
            source_service.update_source(
                WorkCsv.model_validate_json(work.model_dump_json())
            ).model_dump()
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
        works, available_filters = (
            self.repository.get_research_products_by_author(
                author_id=author_id, skip=skip, limit=limit, sort=sort, filters=filters
            )
        )
        total_works = self.repository.count_papers_by_author(
            author_id=author_id, filters=filters
        )
        data = [
            self.update_authors_external_ids(
                WorkListApp.model_validate_json(work.model_dump_json())
            ).model_dump()
            for work in works
        ]
        return {
            "data": data,
            "total_results": total_works,
            "count": len(data),
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
        works, _ = self.repository.get_research_products_by_author(
            author_id=author_id, sort=sort, skip=skip, limit=limit
        )
        return [
            WorkCsv.model_validate_json(work.model_dump_json()).model_dump()
            for work in works
        ]

    def get_research_products_by_author_json(
        self,
        *,
        author_id: str,
        sort: str | None = "title",
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        works, _ = self.repository.get_research_products_by_author(
            author_id=author_id, sort=sort, skip=skip, limit=limit
        )
        return [
            WorkSchema.model_validate_json(work.model_dump_json()).model_dump()
            for work in works
        ]

    def search_api(self, *, params: WorkQueryParams) -> dict[str, Any]:
        works, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            search=params.get_search,
        )
        results = GeneralMultiResponse[WorkSchema](
            total_results=count, page=params.page
        )
        data = [
            WorkSchema.model_validate_json(work.model_dump_json()) for work in works
        ]
        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True))


work_service = WorkService(WorkListApp, WorkProccessed)

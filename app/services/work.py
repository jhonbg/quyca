from typing import Any

from services.base import ServiceBase
from schemas.work import WorkQueryParams, WorkSearch, WorkProccessed
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.repositories.work import (
    WorkRepository,
    work_repository,
)
from services.person import person_service
from services.source import source_service


class WorkService(
    ServiceBase[Work, WorkRepository, WorkQueryParams, WorkSearch, WorkProccessed]
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

    def get_info(self, *, id: str) -> dict[str, Any]:
        work = super().get_by_id(id=id)
        self.update_authors_external_ids(work)
        self.update_source(work)
        return {"data": work.model_dump(exclude_none=True, exclude={"titles"})}


work_service = WorkService(work_repository, WorkSearch, WorkProccessed)

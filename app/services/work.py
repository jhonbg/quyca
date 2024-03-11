from services.base import ServiceBase
from schemas.work import WorkQueryParams, WorkSearch
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.repositories.work import (
    WorkRepository,
    work_repository,
)


class WorkService(ServiceBase[Work, WorkRepository, WorkQueryParams, Work]):
    ...


work_service = WorkService(work_repository, WorkSearch)

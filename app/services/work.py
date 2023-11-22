from services.base import ServiceBase
from schemas.work import WorkQueryParams
from infraestructure.mongo.models.work import Work
from infraestructure.mongo.repositories.work import (
    WorkRepository,
    work_repository,
)


class WorkService(ServiceBase[Work, WorkRepository, WorkQueryParams]):
    ...


work_service = WorkService(work_repository)

from infraestructure.mongo.repositories.base import RepositorieBase
from infraestructure.mongo.models.work import Work


class WorkRepository(RepositorieBase):
    ...

work_repository = WorkRepository(Work)
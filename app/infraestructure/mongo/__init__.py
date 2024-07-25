from typing import NoReturn


from services.affiliation import affiliation_service
from services.plots.affiliation import affiliation_plots_service
from .repositories import (
    affiliation_repository,
    affiliation_calculations_repository,
    work_repository,
    person_repository,
    source_repository,
)



def init_mongo_infraestructure() -> NoReturn:
    affiliation_service.register_repository(repository=affiliation_repository)
    affiliation_service.register_calculations_repository(
        repository=affiliation_calculations_repository
    )
    affiliation_plots_service.register_work_observer(repository=work_repository)
    affiliation_plots_service.register_affiliation_observer(repository=affiliation_repository)

from typing import NoReturn


from services import affiliation_service, person_service, work_service, source_service
from services.plots.affiliation import affiliation_plots_service
from services.plots.person import person_plots_service
from .repositories import (
    affiliation_repository,
    affiliation_calculations_repository,
    work_repository,
    person_repository,
    source_repository,
)



def init_mongo_infraestructure() -> NoReturn:
    # Affiliation
    affiliation_service.register_repository(repository=affiliation_repository)
    affiliation_service.register_calculations_repository(
        repository=affiliation_calculations_repository
    )
    affiliation_service.register_works_repository(repository=work_repository)
    affiliation_service.register_person_repository(repository=person_repository)
    affiliation_plots_service.register_work_observer(repository=work_repository)
    affiliation_plots_service.register_affiliation_observer(repository=affiliation_repository)

    # Person
    person_service.register_repository(repository=person_repository)
    person_service.register_works_repository(repository=work_repository)
    person_service.register_affiliation_repository(repository=affiliation_repository)
    person_plots_service.register_work_observer(repository=work_repository)
    # Work
    work_service.register_repository(repository=work_repository)

    # Source
    source_service.register_repository(repository=source_repository)


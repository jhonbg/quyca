from services.base import ServiceBase
from schemas.affiliation import AffiliationQueryParams, AffiliationSearch
from infraestructure.mongo.models.affiliation import Affiliation
from infraestructure.mongo.repositories.affiliation import (
    AffiliationRepository,
    affiliation_repository,
)


class AffiliationService(
    ServiceBase[
        Affiliation, AffiliationRepository, AffiliationQueryParams, AffiliationSearch
    ]
): ...


affiliation_service = AffiliationService(affiliation_repository, AffiliationSearch)

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import Affiliation


class AffiliationRepository(RepositoryBase):
    ...

affiliation_repository = AffiliationRepository(Affiliation)
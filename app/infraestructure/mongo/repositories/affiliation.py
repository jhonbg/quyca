from infraestructure.mongo.repositories.base import RepositorieBase
from infraestructure.mongo.models.affiliation import Affiliation


class AffiliationRepository(RepositorieBase):
    ...

affiliation_repository = AffiliationRepository(Affiliation)
from protocols.mongo.repositories.base import RepositoryBase
from protocols.mongo.models.affiliation import AffiliationCalculations
from protocols.mongo.utils.iterators import AffiliationCalculationsIterator


class AffiliationCalculationsRepository(
    RepositoryBase[AffiliationCalculations, AffiliationCalculationsIterator]
):
    ...

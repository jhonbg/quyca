from quyca.protocols.mongo.repositories.base import RepositoryBase
from quyca.protocols.mongo.models.affiliation import AffiliationCalculations
from quyca.protocols.mongo.utils.iterators import AffiliationCalculationsIterator


class AffiliationCalculationsRepository(
    RepositoryBase[AffiliationCalculations, AffiliationCalculationsIterator]
):
    ...
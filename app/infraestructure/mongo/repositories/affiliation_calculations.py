from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import AffiliationCalculations
from infraestructure.mongo.utils.iterators import AffiliationCalculationsIterator
from infraestructure.mongo.utils.session import engine_calculations


class AffiliationCalculationsRepository(
    RepositoryBase[AffiliationCalculations, AffiliationCalculationsIterator]
): ...


affiliation_calculations_repository = AffiliationCalculationsRepository(
    AffiliationCalculations, AffiliationCalculationsIterator, engine=engine_calculations
)

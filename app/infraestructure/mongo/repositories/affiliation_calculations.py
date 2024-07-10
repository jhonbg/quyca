from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import AffiliationCalculations
from infraestructure.mongo.utils.iterators import AffiliationCalculationsIterator
from infraestructure.mongo.utils.session import engine_calculations


class AffiliationCalculationsRepository(
    RepositoryBase[AffiliationCalculations, AffiliationCalculationsIterator]
):
    def get_by_id(self, *, id: str) -> AffiliationCalculations | None:
        with self.engine.session() as session:
            results = session.find_one(
                AffiliationCalculations, AffiliationCalculations.id == ObjectId(id)
            )
        return results


affiliation_calculations_repository = AffiliationCalculationsRepository(
    AffiliationCalculations, AffiliationCalculationsIterator, engine=engine_calculations
)

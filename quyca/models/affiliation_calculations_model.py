from pydantic import BaseModel, Field

from models.base_model import PyObjectId, CitationsCount, CoauthorshipNetwork, TopWord


class AffiliationCalculations(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    coauthorship_network: CoauthorshipNetwork | None = None
    top_words: list[TopWord]
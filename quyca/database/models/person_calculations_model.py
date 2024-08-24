from pydantic import BaseModel, Field

from database.models.base_model import PyObjectId, CitationsCount, CoauthorshipNetwork, TopWord


class PersonCalculations(BaseModel):
    id: PyObjectId = Field(alias='_id')
    citations_count: list[CitationsCount] | None = None
    coauthorship_network: CoauthorshipNetwork | None = None
    top_words: list[TopWord]
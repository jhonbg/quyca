from typing import List, Optional

from pydantic import BaseModel, Field

from models.base_model import PyObjectId, CitationsCount


class PersonCalculations(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    citations_count: Optional[List[CitationsCount]] = Field(default_factory=List)
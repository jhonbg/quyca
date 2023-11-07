from typing import Protocol
from datetime import datetime


class BaseModel(Protocol):
    id: int
    created_at: datetime
    updated_at: datetime
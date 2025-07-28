from datetime import datetime
from pydantic import BaseModel, HttpUrl


class News(BaseModel):
    url_id: str | None = None
    medium_id: str | None = None
    url: HttpUrl | None = None
    url_title: str | None = None
    url_language: str | None = None
    url_date: datetime | None = None
    medium: HttpUrl | None = None

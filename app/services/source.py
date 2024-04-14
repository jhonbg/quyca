from services.base import ServiceBase
from schemas.source import SourceQueryParams, Source as SourceSearch
from infraestructure.mongo.models.source import Source
from infraestructure.mongo.repositories.source import (
    SourceRepository,
    source_repository,
)


class SourceService(
    ServiceBase[Source, SourceRepository, SourceQueryParams, SourceSearch, SourceSearch]
): ...


source_service = SourceService(source_repository, SourceSearch, SourceSearch)

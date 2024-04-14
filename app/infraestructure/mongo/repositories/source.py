from infraestructure.mongo.models.source import Source
from infraestructure.mongo.repositories.base import RepositoryBase


class SourceRepository(RepositoryBase[Source]):
    ...

source_repository = SourceRepository(Source)
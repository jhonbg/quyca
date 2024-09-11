from infraestructure.mongo.models.source import Source
from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.utils.iterators import SourceIterator


class SourceRepository(RepositoryBase[Source, SourceIterator]):
    ...


source_repository = SourceRepository(Source, iterator=SourceIterator)

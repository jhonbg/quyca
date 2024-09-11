from protocols.mongo.models.source import Source
from protocols.mongo.repositories.base import RepositoryBase
from protocols.mongo.utils.iterators import SourceIterator


class SourceRepository(RepositoryBase[Source, SourceIterator]):
    ...

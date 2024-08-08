from quyca.protocols.mongo.models.source import Source
from quyca.protocols.mongo.repositories.base import RepositoryBase
from quyca.protocols.mongo.utils.iterators import SourceIterator


class SourceRepository(RepositoryBase[Source, SourceIterator]):
    ...
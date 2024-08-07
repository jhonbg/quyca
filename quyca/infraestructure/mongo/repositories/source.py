from quyca.infraestructure.mongo.models.source import Source
from quyca.infraestructure.mongo.repositories.base import RepositoryBase
from quyca.infraestructure.mongo.utils.iterators import SourceIterator


class SourceRepository(RepositoryBase[Source, SourceIterator]):
    ...

source_repository = SourceRepository(Source, iterator=SourceIterator)
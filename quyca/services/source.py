from quyca.services.base import ServiceBase
from quyca.schemas.source import SourceQueryParams, Source as SourceSearch
from quyca.schemas.work import WorkProccessed
from quyca.protocols.mongo.models.source import Source
from quyca.protocols.mongo.repositories.source import SourceRepository


class SourceService(
    ServiceBase[Source, SourceRepository, SourceQueryParams, SourceSearch, SourceSearch]
): 
    def update_source(self, work: WorkProccessed):
        if work.source.id:
            source = self.get_by_id(id=work.source.id)
            serials = {}
            for serial in source.external_ids:
                serials[serial.source] = serial.id
            work.source.serials = serials
            work.source.scimago_quartile = source.scimago_quartile
        return work



source_service = SourceService(SourceSearch, SourceSearch)

from database.models.base_model import ExternalId
from database.models.source_model import Source
from database.models.work_model import Work
from database.repositories import source_repository


def update_work_source(work: Work):
    source = source_repository.get_source_by_id(work.source.id)
    set_source_serials(work, source)
    set_source_scimago_quartile(work, source)

def set_source_scimago_quartile(work: Work, source: Source):
    for ranking in source.ranking:
        condition = (
                ranking.source == "scimago Best Quartile" and
                ranking.rank != "-" and
                ranking.from_date <= work.date_published <= ranking.to_date
        )
        if condition:
            work.source.scimago_quartile = ranking.rank
            break

def set_source_serials(work: Work, source: Source):
    serials = {}
    for external_id in source.external_ids:
        serials[external_id.source] = external_id.id
    work.source.serials = serials

def set_source_fields(work: Work):
    doi = next(filter(lambda external_id: external_id.source == "doi", work.external_ids), ExternalId())
    work.doi = doi.id
    work.source_name = work.source.name
    work.scimago_quartile = work.source.scimago_quartile

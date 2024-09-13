from database.models.source_model import Source
from database.models.work_model import Work
from database.repositories import source_repository


def update_work_source(work: Work):
    if work.source.id:
        source = source_repository.get_source_by_id(work.source.id)
        set_serials(work, source)
        set_scimago_quartile(work, source)


def update_csv_work_source(work: Work):
    if work.source.id:
        source_data = work.source_data
        set_csv_scimago_quartile(work, source_data)
        set_source_urls(work, source_data)
        if source_data.publisher:
            work.publisher = str(source_data.publisher.name)
        if source_data.apc.charges and source_data.apc.currency:
            work.source_apc = (
                str(source_data.apc.charges) + " / " + str(source_data.apc.currency)
            )
        work.source_name = work.source.name


def set_source_urls(work, source):
    source_urls = []
    for external_url in source.external_urls:
        source_urls.append(str(external_url.url))
    work.source_urls = " | ".join(set(source_urls))


def set_scimago_quartile(work: Work, source: Source):
    if source.ranking:
        for ranking in source.ranking:
            condition = (
                ranking.source == "scimago Best Quartile"
                and ranking.rank != "-"
                and work.date_published
                and ranking.from_date <= work.date_published <= ranking.to_date
            )
            if condition:
                work.source.scimago_quartile = ranking.rank
                break


def set_csv_scimago_quartile(work: Work, source: Source):
    for ranking in source.ranking:
        condition = (
            ranking.source == "scimago Best Quartile"
            and ranking.rank != "-"
            and work.date_published
            and ranking.from_date <= work.date_published <= ranking.to_date
        )
        if condition:
            work.scimago_quartile = ranking.rank
            break


def set_serials(work: Work, source: Source):
    if source.external_ids:
        serials = {}
        for external_id in source.external_ids:
            serials[external_id.source] = external_id.id
        work.source.serials = serials

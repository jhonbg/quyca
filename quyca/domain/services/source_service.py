from domain.models.source_model import Source
from domain.models.work_model import Work
from infrastructure.repositories import source_repository
from quyca.domain.models.base_model import QueryParams
from typing import Dict
from quyca.domain.parsers import source_parser


def update_work_source(work: Work) -> None:
    if work.source.id:
        source = source_repository.get_source_by_id(work.source.id)
        set_serials(work, source)
        set_scimago_quartile(work, source)


def update_csv_work_source(work: Work) -> None:
    if work.source.id:
        source_data = work.source_data[0]
        set_csv_scimago_quartile(work, source_data)
        set_source_urls(work, source_data)
        if source_data.publisher:
            work.publisher = str(source_data.publisher.name)
        if source_data.apc.charges and source_data.apc.currency:
            work.source_apc = str(source_data.apc.charges) + " / " + str(source_data.apc.currency)
        work.source_name = work.source.name


def set_source_urls(work: Work, source: Source) -> None:
    source_urls = []
    for external_url in source.external_urls:
        source_urls.append(str(external_url.url))
    work.source_urls = " | ".join(set(source_urls))


def set_scimago_quartile(work: Work, source: Source) -> None:
    if work.source:
        work.source.scimago_quartile = ""
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


def set_csv_scimago_quartile(work: Work, source: Source) -> None:
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


def set_serials(work: Work, source: Source) -> None:
    if source.external_ids:
        external_ids = {}
        for external_id in source.external_ids:
            external_ids[external_id.source] = external_id.id
        work.source.external_ids = external_ids


def search_sources(query_params: QueryParams) -> Dict:
    """
    Searches for sources based on the provided query parameters. Parameter keyword inside the query parameters is used for search by name.

    Parameters:
    -----------
    query_params : QueryParams
        The query parameters to filter the sources.

    Returns:
    --------
    Dict
        A dictionary containing the search data and the total number of results.
    """
    pipeline_params = get_sources_by_entity_pipeline_params()
    sources, total_sources = source_repository.search_sources(query_params, pipeline_params)
    source_list = []
    for source in sources:
        source_list.append(source)

    data = source_parser.parse_sources_by_entity(source_list)

    return {"data": data, "total_results": total_sources}


def get_sources_by_entity_pipeline_params() -> Dict:
    """
    Returns:
    --------
    Dictionary
    This function retrieves a Dictionary with the params that must include each document
    """
    pipeline_source_params = {
        "source": [
            "_id",
            "updated",
            "names",
            "abbreviations",
            "types",
            "keywords",
            "languages",
            "publisher",
            "relations",
            "addresses",
            "external_ids",
            "external_urls",
            "waiver",
            "plagiarism_detection",
            "open_access_start_year",
            "publication_time_weeks",
            "apc",
            "copyright",
            "licenses",
            "subjects",
            "ranking",
            "review_process",
        ]
    }

    return pipeline_source_params

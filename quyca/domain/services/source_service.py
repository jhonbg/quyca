from infrastructure.repositories import source_repository
from quyca.domain.models.base_model import QueryParams
from quyca.domain.parsers import source_parser


def get_source_by_id(source_id: str) -> dict:
    """
    Retrieves a source by its ID.

    Parameters:
    -----------
    source_id : str
        The ID of the source to retrieve.

    Returns:
    --------
    dict
        A dictionary representation of the source.
    """
    source = source_repository.get_source_by_id(source_id)
    data = source_parser.parse_source(source)
    return {"data": data}


def search_sources(query_params: QueryParams) -> dict:
    """
    Searches for sources based on the provided query parameters. Parameter keyword inside the query parameters is used for search by name.

    Parameters:
    -----------
    query_params : QueryParams
        The query parameters to filter the sources.

    Returns:
    --------
    dict
        A dictionary containing the search data and the total number of results.
    """
    pipeline_params = get_sources_by_entity_pipeline_params()
    sources, total_sources = source_repository.search_sources(query_params, pipeline_params)
    source_list = []
    for source in sources:
        source_list.append(source)

    data = source_parser.parse_search_result(source_list)

    return {"data": data, "total_results": total_sources}


def get_search_sources_available_filters(query_params: QueryParams) -> dict:
    """
    Retrieves the available filters for searching sources based on the provided query parameters.

    Parameters:
    -----------
    query_params : QueryParams
        The query parameters to filter the sources.

    Returns:
    --------
    dict
        A dictionary containing the available filters for source search.
    """
    available_filters = source_repository.get_search_sources_available_filters(query_params)
    return source_parser.parse_available_filters(available_filters)


def get_sources_by_entity_pipeline_params() -> dict:
    """
    Returns:
    --------
    dictionary
    This function retrieves a dictionary with the params that gonna be used for searching.
    """
    pipeline_source_params = {
        "source": [
            "names",
            "types",
            "keywords",
            "publisher",
            "external_ids",
            "external_urls",
            "subjects",
            "ranking",
        ],
        "collection": "sources",
    }

    return pipeline_source_params

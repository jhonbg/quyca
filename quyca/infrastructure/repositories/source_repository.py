from typing import Dict, Generator, Tuple
from bson import ObjectId

from infrastructure.mongo import database
from infrastructure.repositories import base_repository
from infrastructure.generators import source_generator
from domain.models.source_model import Source
from domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.models.base_model import QueryParams


def get_source_by_id(source_id: str) -> Source:
    source_data = database["sources"].find_one({"_id": ObjectId(source_id)})
    if not source_data:
        raise NotEntityException(f"The source with id {source_id} does not exist.")
    return Source(**source_data)

def search_sources(query_params: QueryParams, pipeline_params: Dict) -> Tuple[Generator, int]:
    """
    Parameters:
    -----------
    query_params : QueryParams
        The query parameters containing keywords and other filters for the search.
    pipeline_params : Dict
        The pipeline parameters for the MongoDB aggregation pipeline.

    Returns:
    --------
    Tuple[Generator, int]
        A tuple containing a generator for the search results and the total number of results.
    """
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    sources = database["sources"].aggregate(pipeline)

    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []

    count_pipeline += [{"$count": "total_results"}]
    total_results = next(database["sources"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return source_generator.get(sources), total_results

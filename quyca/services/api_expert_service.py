from database.models.base_model import QueryParams
from database.repositories import work_repository
from services.parsers import work_parser


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params)
    data = work_parser.parse_api_expert(works)
    return {"data": data}

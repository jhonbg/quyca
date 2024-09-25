from domain.models.base_model import QueryParams
from infrastructure.repositories import work_repository
from domain.parsers import work_parser


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params)
    data = work_parser.parse_api_expert(works)
    return {"data": data}


def get_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_person(person_id, query_params)
    data = work_parser.parse_api_expert(works)
    return {"data": data}

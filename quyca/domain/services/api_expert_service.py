from typing import Generator

from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.repositories import api_expert_repository
from quyca.domain.parsers import work_parser


def get_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    works = api_expert_repository.get_works_by_person_for_api_expert(person_id, query_params)
    data = process_works(works)
    return {"data": data}


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    works = api_expert_repository.get_works_by_affiliation_for_api_expert(affiliation_id, query_params)
    data = process_works(works)
    return {"data": data}


def search_works(query_params: QueryParams) -> dict:
    works = api_expert_repository.search_works_for_api_expert(query_params)
    data = process_works(works)
    return {"data": data}


def process_works(works: Generator) -> list:
    works_list = list(works)
    data = work_parser.parse_api_expert(works_list)
    return data

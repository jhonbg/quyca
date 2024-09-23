from typing import Generator

from database.models.base_model import QueryParams
from database.repositories import other_work_repository
from services.base_service import (
    set_external_ids,
    set_external_urls,
    set_authors_external_ids,
    limit_authors,
    set_product_types,
    set_title_and_language,
)
from services.parsers import other_work_parser


def get_other_work_by_id(other_work_id: str) -> dict:
    other_work = other_work_repository.get_other_work_by_id(other_work_id)
    set_external_ids(other_work)
    set_external_urls(other_work)
    limit_authors(other_work)
    set_authors_external_ids(other_work)
    set_title_and_language(other_work)
    set_product_types(other_work)
    data = other_work_parser.parse_other_work(other_work)
    return {"data": data}


def get_other_work_authors(other_work_id: str) -> dict:
    other_work = other_work_repository.get_other_work_by_id(other_work_id)
    set_authors_external_ids(other_work)
    return {"data": other_work.model_dump()["authors"]}


def search_other_works(query_params: QueryParams) -> dict:
    pipeline_params = get_other_works_by_entity_pipeline_params()
    other_works, total_results = other_work_repository.search_other_works(query_params, pipeline_params)
    other_works_data = get_other_work_by_entity_data(other_works)
    data = other_work_parser.parse_search_results(other_works_data)
    return {"data": data, "total_results": total_results}


def get_other_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_other_works_by_entity_pipeline_params()
    other_works = other_work_repository.get_other_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    other_works_data = get_other_work_by_entity_data(other_works)
    data = other_work_parser.parse_other_works_by_entity(other_works_data)
    total_results = other_work_repository.get_other_works_count_by_affiliation(affiliation_id)
    return {"data": data, "total_results": total_results}


def get_other_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_other_works_by_entity_pipeline_params()
    other_works = other_work_repository.get_other_works_by_person(person_id, query_params, pipeline_params)
    other_works_data = get_other_work_by_entity_data(other_works)
    data = other_work_parser.parse_other_works_by_entity(other_works_data)
    total_results = other_work_repository.get_other_works_count_by_person(person_id)
    return {"data": data, "total_results": total_results}


def get_other_work_by_entity_data(other_works: Generator) -> list:
    other_works_data = []
    for other_work in other_works:
        limit_authors(other_work)
        set_title_and_language(other_work)
        set_product_types(other_work)
        other_works_data.append(other_work)
    return other_works_data


def get_other_works_by_entity_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "authors",
            "types",
            "titles",
            "subjects",
            "year_published",
            "external_ids",
            "external_urls",
            "authors_data",
        ]
    }
    return pipeline_params

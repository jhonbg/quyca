from typing import Generator

from quyca.domain.models.base_model import QueryParams
from quyca.domain.models.work_model import Work, Abstract
from quyca.infrastructure.repositories import work_repository
from quyca.domain.services import source_service
from quyca.domain.services.base_service import (
    limit_authors,
    set_title_and_language,
    set_product_types,
    set_authors_external_ids,
    set_external_urls,
    set_external_ids,
)
from quyca.domain.parsers import work_parser


def get_work_by_id(work_id: str) -> dict:
    work = work_repository.get_work_by_id(work_id)
    set_abstract(work)
    set_external_ids(work)
    set_external_urls(work)
    limit_authors(work)
    set_authors_external_ids(work)
    source_service.update_work_source(work)
    set_title_and_language(work)
    set_product_types(work)
    data = work_parser.parse_work(work)
    return {"data": data}


def set_abstract(work: Work) -> None:
    def order(abstract: Abstract) -> float:
        hierarchy = ["openalex", "scholar", "scienti"]
        return hierarchy.index(abstract.source) if abstract.source in hierarchy else float("inf")

    if not work.abstracts:
        return
    first_abstract = sorted(work.abstracts, key=order)[0]
    work.abstract = first_abstract.abstract


def get_work_authors(work_id: str) -> dict:
    work = work_repository.get_work_by_id(work_id)
    set_authors_external_ids(work)
    return {"data": work.model_dump()["authors"]}


def search_works(query_params: QueryParams) -> dict:
    pipeline_params = get_works_by_entity_pipeline_params()
    works, total_results = work_repository.search_works(query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_search_results(works_data)
    return {"data": data, "total_results": total_results}


def get_search_works_available_filters(query_params: QueryParams) -> dict:
    available_filters = work_repository.get_search_works_available_filters(query_params)
    return work_parser.parse_available_filters(available_filters)


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_works_by_entity_pipeline_params()
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_works_by_entity(works_data)
    total_results = work_repository.get_works_count_by_affiliation(affiliation_id, query_params)
    return {"data": data, "total_results": total_results}


def get_works_filters_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    available_filters = work_repository.get_works_available_filters_by_affiliation(affiliation_id, query_params)
    return work_parser.parse_available_filters(available_filters)


def get_works_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_works_by_entity_pipeline_params()
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_works_by_entity(works_data)
    total_results = work_repository.get_works_count_by_person(person_id, query_params)
    return {"data": data, "total_results": total_results}


def get_works_filters_by_person(person_id: str, query_params: QueryParams) -> dict:
    available_filters = work_repository.get_works_available_filters_by_person(person_id, query_params)
    return work_parser.parse_available_filters(available_filters)


def get_work_by_entity_data(works: Generator) -> list:
    works_data = []
    for work in works:
        limit_authors(work)
        set_title_and_language(work)
        set_product_types(work)
        works_data.append(work)
    return works_data


def get_works_by_entity_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "author_count",
            "open_access",
            "authors.full_name",
            "authors.id",
            "authors.affiliations.id",
            "authors.affiliations.name",
            "authors.affiliations.types",
            "citations_count",
            "bibliographic_info",
            "types",
            "source",
            "titles",
            "subjects",
            "year_published",
            "external_ids",
            "external_urls",
            "ranking",
            "topics",
        ]
    }
    return pipeline_params

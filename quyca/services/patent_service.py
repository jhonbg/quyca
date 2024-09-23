from typing import Generator

from database.models.base_model import QueryParams
from database.repositories import patent_repository
from services.base_service import (
    set_external_ids,
    set_external_urls,
    set_authors_external_ids,
    limit_authors,
    set_product_types,
    set_title_and_language,
)
from services.parsers import patent_parser


def get_patent_by_id(patent_id: str) -> dict:
    patent = patent_repository.get_patent_by_id(patent_id)
    set_external_ids(patent)
    set_external_urls(patent)
    limit_authors(patent)
    set_authors_external_ids(patent)
    set_title_and_language(patent)
    set_product_types(patent)
    data = patent_parser.parse_patent(patent)
    return {"data": data}


def get_patent_authors(patent_id: str) -> dict:
    patent = patent_repository.get_patent_by_id(patent_id)
    set_authors_external_ids(patent)
    return {"data": patent.model_dump()["authors"]}


def search_patents(query_params: QueryParams) -> dict:
    pipeline_params = get_patents_by_entity_pipeline_params()
    patents, total_results = patent_repository.search_patents(query_params, pipeline_params)
    patents_data = get_patent_by_entity_data(patents)
    data = patent_parser.parse_search_results(patents_data)
    return {"data": data, "total_results": total_results}


def get_patents_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_patents_by_entity_pipeline_params()
    patents = patent_repository.get_patents_by_affiliation(affiliation_id, query_params, pipeline_params)
    patents_data = get_patent_by_entity_data(patents)
    data = patent_parser.parse_patents_by_entity(patents_data)
    total_results = patent_repository.get_patents_count_by_affiliation(affiliation_id)
    return {"data": data, "total_results": total_results}


def get_patents_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_patents_by_entity_pipeline_params()
    patents = patent_repository.get_patents_by_person(person_id, query_params, pipeline_params)
    patents_data = get_patent_by_entity_data(patents)
    data = patent_parser.parse_patents_by_entity(patents_data)
    total_results = patent_repository.get_patents_count_by_person(person_id)
    return {"data": data, "total_results": total_results}


def get_patent_by_entity_data(patents: Generator) -> list:
    patents_data = []
    for patent in patents:
        limit_authors(patent)
        set_title_and_language(patent)
        set_product_types(patent)
        patents_data.append(patent)
    return patents_data


def get_patents_by_entity_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "authors",
            "types",
            "titles",
            "subjects",
            "external_ids",
            "external_urls",
            "authors_data",
        ]
    }
    return pipeline_params

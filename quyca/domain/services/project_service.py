from typing import Generator

from domain.models.base_model import QueryParams
from infrastructure.repositories import project_repository
from domain.services.base_service import (
    set_external_ids,
    set_external_urls,
    set_authors_external_ids,
    limit_authors,
    set_product_types,
    set_title_and_language,
)
from domain.parsers import project_parser


def get_project_by_id(project_id: str) -> dict:
    project = project_repository.get_project_by_id(project_id)
    set_external_ids(project)
    set_external_urls(project)
    limit_authors(project)
    set_authors_external_ids(project)
    set_title_and_language(project)
    set_product_types(project)
    data = project_parser.parse_project(project)
    return {"data": data}


def get_project_authors(project_id: str) -> dict:
    project = project_repository.get_project_by_id(project_id)
    set_authors_external_ids(project)
    return {"data": project.model_dump()["authors"]}


def search_projects(query_params: QueryParams) -> dict:
    pipeline_params = get_projects_by_entity_pipeline_params()
    projects, total_results = project_repository.search_projects(query_params, pipeline_params)
    projects_data = get_project_by_entity_data(projects)
    data = project_parser.parse_search_results(projects_data)
    return {"data": data, "total_results": total_results}


def get_projects_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_projects_by_entity_pipeline_params()
    projects = project_repository.get_projects_by_affiliation(affiliation_id, query_params, pipeline_params)
    projects_data = get_project_by_entity_data(projects)
    data = project_parser.parse_projects_by_entity(projects_data)
    total_results = project_repository.get_projects_count_by_affiliation(affiliation_id)
    return {"data": data, "total_results": total_results}


def get_projects_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = get_projects_by_entity_pipeline_params()
    projects = project_repository.get_projects_by_person(person_id, query_params, pipeline_params)
    projects_data = get_project_by_entity_data(projects)
    data = project_parser.parse_projects_by_entity(projects_data)
    total_results = project_repository.get_projects_count_by_person(person_id)
    return {"data": data, "total_results": total_results}


def get_project_by_entity_data(projects: Generator) -> list:
    projects_data = []
    for project in projects:
        limit_authors(project)
        set_title_and_language(project)
        set_product_types(project)
        projects_data.append(project)
    return projects_data


def get_projects_by_entity_pipeline_params() -> dict:
    pipeline_params = {
        "project": [
            "_id",
            "author_count",
            "authors",
            "types",
            "titles",
            "subjects",
            "year_init",
            "year_end",
            "external_ids",
            "external_urls",
            "authors_data",
        ]
    }
    return pipeline_params

from domain.models.project_model import Project


def parse_search_results(projects: list) -> list:
    include = [
        "id",
        "authors",
        "author_count",
        "product_types",
        "year_init",
        "year_end",
        "title",
        "external_ids",
        "external_urls",
    ]
    return [project.model_dump(include=include) for project in projects]


def parse_projects_by_entity(projects: list) -> list:
    include = [
        "id",
        "authors",
        "author_count",
        "product_types",
        "year_init",
        "year_end",
        "title",
        "external_ids",
    ]
    return [project.model_dump(include=include) for project in projects]


def parse_project(project: Project) -> dict:
    return project.model_dump()

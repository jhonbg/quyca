from infrastructure.repositories import (
    info_repository,
)


def get_info() -> dict:
    return {
        "db_update": info_repository.get_last_db_update(),
        "total_products": info_repository.get_entity_count("works"),
        "total_institutions": info_repository.get_entity_count("affiliations", "institution"),
        "total_faculties": info_repository.get_entity_count("affiliations", "faculty"),
        "total_departments": info_repository.get_entity_count("affiliations", "department"),
        "total_groups": info_repository.get_entity_count("affiliations", "group"),
        "total_patents": info_repository.get_entity_count("patents"),
        "total_projects": info_repository.get_entity_count("projects"),
        "total_other_products": info_repository.get_entity_count("works_misc"),
        "total_authors": info_repository.get_entity_count("person"),
    }

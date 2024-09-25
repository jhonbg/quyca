from infrastructure.repositories import etl_repository


def set_person_products_count() -> None:
    etl_repository.set_person_products_count()


def set_person_citations_count() -> None:
    etl_repository.set_person_citations_count()

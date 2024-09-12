from database.repositories import etl_repository


def set_person_products_count():
    etl_repository.set_person_products_count()


def set_person_citations_count():
    etl_repository.set_person_citations_count()

from domain.models.other_work_model import OtherWork


def parse_search_results(other_works: list) -> list:
    include = [
        "id",
        "authors",
        "product_types",
        "year_published",
        "title",
        "external_ids",
        "external_urls",
    ]
    return [other_work.model_dump(include=include) for other_work in other_works]


def parse_other_works_by_entity(other_works: list) -> list:
    include = [
        "id",
        "authors",
        "product_types",
        "year_published",
        "title",
        "external_ids",
    ]
    return [other_work.model_dump(include=include) for other_work in other_works]


def parse_other_work(other_work: OtherWork) -> dict:
    return other_work.model_dump()

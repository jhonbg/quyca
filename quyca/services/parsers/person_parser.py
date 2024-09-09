def parse_search_result(persons: list) -> list:
    include = [
        "id",
        "full_name",
        "affiliations",
        "external_ids",
        "products_count",
        "citations_count",
    ]
    return [person.model_dump(include=include, exclude_none=True) for person in persons]


def parse_person(person):
    include = [
        "id",
        "full_name",
        "affiliations",
        "external_ids",
        "products_count",
        "citations_count",
        "logo",
    ]
    return person.model_dump(include=include, exclude_none=True)

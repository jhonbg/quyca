def parse_search_result(affiliations: list) -> list:
    include = [
        "id",
        "addresses",
        "affiliations",
        "external_ids",
        "external_urls",
        "products_count",
        "citations_count",
        "logo",
        "name",
        "types",
        "products_count",
        "ranking",
    ]
    return [affiliation.model_dump(include=include, exclude_none=True) for affiliation in affiliations]

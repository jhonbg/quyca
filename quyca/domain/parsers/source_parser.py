from typing import List

def parse_sources_by_entity(sources: List) -> List:
    source_fields = [
        "_id",
        "names",
        "types",
        "addresses",
        "external_ids",
        "external_urls",
        "apc",
        "subjects",
        "ranking",
    ]

    return [source.model_dump(include=source_fields) for source in sources]

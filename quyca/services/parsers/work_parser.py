import csv
import io


def parse_csv(works: list):
    include = [
        "titles",
        "authors",
        "institutions",
        "faculties",
        "departments",
        "groups",
        "groups_ranking",
        "issue",
        "is_open_access",
        "open_access_status",
        "start_page",
        "end_page",
        "volume",
        "scimago_quartile",
        "openalex_citations_count",
        "scholar_citations_count",
        "subjects",
        "date_published",
        "doi",
        "publisher",
        "openalex_types",
        "scienti_types",
        "source_name",
        "source_apc",
        "source_languages",
        "source_urls",
    ]
    works_dict = [work.model_dump(include=include) for work in works]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=include)
    writer.writeheader()
    writer.writerows(works_dict)
    return output.getvalue()

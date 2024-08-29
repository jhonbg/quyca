import csv
import io


def parse_csv(works: list):
    include = [
        "titles",
        "abstract",
        "authors",
        "affiliations",
        "bibtex",
        "issue",
        "is_open_access",
        "open_access_status",
        "pages",
        "start_page",
        "end_page",
        "volume",
        "scimago_quartile",
        "citations_count",
        "groups",
        "subjects",
        "date_published",
        "doi",
        "year_published",
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

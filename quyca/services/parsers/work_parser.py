import csv
import io

from database.models.work_model import Work


def parse_csv(works: list):
    include = [
        "title",
        "language",
        "abstract",
        "authors",
        "institutions",
        "faculties",
        "departments",
        "groups",
        "countries",
        "groups_ranking",
        "ranking",
        "issue",
        "is_open_access",
        "open_access_status",
        "pages",
        "start_page",
        "end_page",
        "volume",
        "bibtex",
        "scimago_quartile",
        "openalex_citations_count",
        "scholar_citations_count",
        "subjects",
        "year_published",
        "doi",
        "publisher",
        "openalex_types",
        "scienti_types",
        "source_name",
        "source_apc",
        "source_urls",
    ]
    works_dict = [work.model_dump(include=include) for work in works]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=include)
    writer.writeheader()
    writer.writerows(works_dict)
    return output.getvalue()


def parse_search_results(works: list):
    include = [
        "id",
        "authors",
        "is_open_access",
        "open_access_status",
        "citations_count",
        "product_types",
        "year_published",
        "title",
        "subjects",
        "source",
        "external_ids",
        "external_urls",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_works_by_entity(works: list):
    include = [
        "id",
        "authors",
        "is_open_access",
        "open_access_status",
        "citations_count",
        "product_types",
        "year_published",
        "title",
        "subjects",
        "source",
        "external_ids",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_work(work: Work):
    exclude_fields = {
        "subtitle": True,
        "titles": True,
        "author_count": True,
        "citations": True,
        "citations_by_year": True,
        "date_published": True,
        "product_types": True,
        "groups": True,
        "keywords": True,
        "ranking": True,
        "references": True,
        "types": True,
        "updated": True,
        "subjects": {"__all__": {"subjects": {"__all__": {"external_ids"}}}},
    }
    return work.model_dump(exclude=exclude_fields, exclude_none=True)

import csv
import io
from typing import Generator

from domain.constants.open_access_status import open_access_status_dict
from domain.constants.product_types import source_titles
from domain.models.work_model import Work


def parse_csv(works: list) -> str:
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
    writer = csv.DictWriter(output, fieldnames=include, escapechar="\\", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(works_dict)
    del works_dict
    return output.getvalue()


def parse_search_results(works: list) -> list:
    include = [
        "id",
        "authors",
        "authors_count",
        "open_access",
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


def parse_works_by_entity(works: list) -> list:
    include = [
        "id",
        "authors",
        "authors_count",
        "open_access",
        "citations_count",
        "product_types",
        "year_published",
        "title",
        "subjects",
        "source",
        "external_ids",
    ]
    return [work.model_dump(include=include, exclude_none=True) for work in works]


def parse_work(work: Work) -> dict:
    return work.model_dump(exclude_none=True)


def parse_api_expert(works: Generator) -> list:
    return [work.model_dump(exclude_none=True) for work in works]


def parse_available_filters(filters: dict) -> dict:
    available_filters: dict = {}
    if product_types := filters.get("product_types"):
        types = parse_product_type_filter(product_types)
        available_filters["product_types"] = types
    if years := filters.get("years"):
        available_filters["years"] = years
    if status := filters.get("status"):
        statuses = parse_status_filter(status)
        available_filters["status"] = statuses
    return available_filters


def parse_status_filter(status: list) -> list:
    statuses = []
    open_children = []
    for oa_status in status:
        if not oa_status.get("_id"):
            statuses.append({"value": "unknown", "title": "Sin información"})
        elif oa_status.get("_id") != "closed":
            open_children.append(
                {"value": oa_status.get("_id"), "title": open_access_status_dict.get(oa_status.get("_id"))}
            )
        else:
            statuses.append({"value": "closed", "title": "Cerrado"})
    if len(open_children) > 0:
        open_children.sort(key=lambda x: x.get("title"))  # type: ignore
        statuses.append({"value": "open", "title": "Abierto", "children": open_children})  # type: ignore
    statuses.sort(key=lambda x: x.get("title"))  # type: ignore
    return statuses


def parse_product_type_filter(product_types: list) -> list:
    types = []
    for product_type in product_types:
        children = []
        if product_type.get("_id") == "crossref":
            continue
        elif product_type.get("_id") == "minciencias":
            for inner_type in product_type.get("types"):
                if inner_type.get("level") == 0:
                    continue
                children.append(
                    {
                        "value": product_type.get("_id") + "_" + inner_type.get("type"),
                        "title": inner_type.get("type"),
                    }
                )
        elif product_type.get("_id") == "scienti":
            second_level_children = []
            third_level_children = []
            for inner_type in product_type.get("types"):
                if inner_type.get("level") == 0:
                    children.append(
                        {
                            "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                            "title": inner_type.get("code") + " " + inner_type.get("type"),
                            "code": inner_type.get("code"),
                            "children": [],
                        }
                    )
                elif inner_type.get("level") == 1:
                    second_level_children.append(
                        {
                            "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                            "title": inner_type.get("code") + " " + inner_type.get("type"),
                            "code": inner_type.get("code"),
                            "children": [],
                        }
                    )
                elif inner_type.get("level") == 2:
                    third_level_children.append(
                        {
                            "value": "scienti_" + inner_type.get("type") + "_" + inner_type.get("code"),
                            "title": inner_type.get("code") + " " + inner_type.get("type"),
                            "code": inner_type.get("code"),
                        }
                    )
            second_level_children.sort(key=lambda x: x.get("title"))  # type: ignore
            third_level_children.sort(key=lambda x: x.get("title"))  # type: ignore
            for child in second_level_children:
                child["children"] = list(
                    filter(lambda x: str(x.get("code")).startswith(str(child.get("code"))), third_level_children)
                )
            for child in children:
                child["children"] = list(
                    filter(lambda x: str(x.get("code")).startswith(str(child.get("code"))), second_level_children)
                )
        else:
            for inner_type in product_type.get("types"):
                children.append(
                    {
                        "value": product_type.get("_id") + "_" + inner_type.get("type"),
                        "title": inner_type.get("type"),
                    }
                )
        children.sort(key=lambda x: x.get("title"))  # type: ignore
        types.append(
            {
                "value": product_type.get("_id"),
                "title": source_titles.get(product_type.get("_id")),
                "children": children,
            }
        )
    return types

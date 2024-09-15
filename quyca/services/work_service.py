from urllib.parse import urlparse

from database.models.base_model import ExternalUrl, QueryParams
from database.models.work_model import Work, Title, ProductType
from database.repositories import person_repository
from database.repositories import work_repository
from enums.external_urls import external_urls_dict
from services import source_service
from services.parsers import work_parser


def get_work_by_id(work_id: str):
    work = work_repository.get_work_by_id(work_id)
    set_external_ids(work)
    set_external_urls(work)
    limit_authors(work)
    set_authors_external_ids(work)
    set_bibliographic_info(work)
    source_service.update_work_source(work)
    set_title_and_language(work)
    set_product_types(work)
    data = work_parser.parse_work(work)
    return {"data": data}


def get_work_authors(work_id: str):
    work = work_repository.get_work_by_id(work_id)
    set_authors_external_ids(work)
    return {"data": work.model_dump()["authors"]}


def search_works(query_params: QueryParams):
    pipeline_params = get_works_by_entity_pipeline_params()
    works, total_results = work_repository.search_works(query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_search_results(works_data)
    return {"data": data, "total_results": total_results}


def get_works_by_affiliation(affiliation_id: str, query_params: QueryParams):
    pipeline_params = get_works_by_entity_pipeline_params()
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_works_by_entity(works_data)
    total_results = work_repository.get_works_count_by_affiliation(affiliation_id)
    return {"data": data, "total_results": total_results}


def get_works_by_person(person_id: str, query_params: QueryParams):
    pipeline_params = get_works_by_entity_pipeline_params()
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    works_data = get_work_by_entity_data(works)
    data = work_parser.parse_works_by_entity(works_data)
    total_results = work_repository.get_works_count_by_person(person_id)
    return {"data": data, "total_results": total_results}


def get_work_by_entity_data(works):
    works_data = []
    for work in works:
        limit_authors(work)
        set_title_and_language(work)
        set_product_types(work)
        set_bibliographic_info(work)
        works_data.append(work)
    return works_data


def get_works_by_entity_pipeline_params():
    pipeline_params = {
        "project": [
            "_id",
            "authors",
            "citations_count",
            "bibliographic_info",
            "types",
            "source",
            "titles",
            "subjects",
            "year_published",
            "external_ids",
            "external_urls",
            "authors_data",
        ]
    }
    return pipeline_params


def set_title_and_language(work: Work):
    def order(title: Title):
        hierarchy = ["openalex", "scholar", "scienti", "minciencias", "ranking"]
        return hierarchy.index(title.source) if title.source in hierarchy else float("inf")

    first_title = sorted(work.titles, key=order)[0]
    work.language = first_title.lang
    work.title = first_title.title


def set_product_types(work: Work):
    def order(product_type: ProductType):
        hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
        return (
            hierarchy.index(product_type.source)
            if product_type.source in hierarchy
            else float("inf")
        )

    product_types = list(
        map(
            lambda product_type: ProductType(name=product_type.type, source=product_type.source),
            work.types,
        )
    )
    work.product_types = sorted(product_types, key=order)


def set_bibliographic_info(work: Work):
    if not work.bibliographic_info:
        return
    work.issue = work.bibliographic_info.issue
    work.open_access_status = work.bibliographic_info.open_access_status
    work.volume = work.bibliographic_info.volume
    work.bibliographic_info = None


def set_authors_external_ids(work: Work):
    if not work.authors:
        return
    for author in work.authors:
        if author.id:
            author.external_ids = person_repository.get_person_by_id(str(author.id)).external_ids


def limit_authors(work: Work, limit: int = 10):
    if not work.authors:
        return
    if len(work.authors) > limit:
        work.authors = work.authors[:limit]


def set_external_ids(work: Work):
    if not work.external_ids:
        return
    new_external_ids = []
    for external_id in work.external_ids:
        if external_id.source in ["minciencias", "scienti"]:
            new_external_ids.append(external_id)
        else:
            work.external_urls.append(ExternalUrl(url=external_id.id, source=external_id.source))
    work.external_ids = list(set(new_external_ids))


def set_external_urls(work: Work):
    if not work.external_urls:
        return
    new_external_urls = []
    for external_url in work.external_urls:
        url = str(external_url.url)
        if urlparse(url).scheme and urlparse(url).netloc:
            new_external_urls.append(external_url)
        else:
            if external_url.source in external_urls_dict.keys() and url != "":
                new_external_urls.append(
                    ExternalUrl(
                        url=external_urls_dict[external_url.source].format(id=url),
                        source=external_url.source,
                    )
                )
    work.external_urls = list(set(new_external_urls))

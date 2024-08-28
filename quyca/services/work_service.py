from urllib.parse import urlparse

from database.models.base_model import ExternalUrl
from database.models.work_model import Work, Title, ProductType
from database.repositories.person_repository import PersonRepository
from database.repositories.work_repository import WorkRepository
from enums.external_urls import external_urls
from services import new_source_service


class WorkService:
    @classmethod
    def get_work_by_id(cls, work_id: str):
        work = WorkRepository.get_work_by_id(work_id)
        cls.set_external_ids(work)
        cls.set_external_urls(work)
        if work.authors:
            cls.limit_authors(work)
            cls.set_authors_external_ids(work)
        if work.bibliographic_info:
            cls.set_bibliographic_info(work)
        if work.source.id:
            new_source_service.update_work_source(work)
        if work.titles:
            cls.set_title_and_language(work)
        if work.types:
            cls.set_product_types(work)
        return work

    @staticmethod
    def set_title_and_language(work: Work):
        def order(title: Title):
            hierarchy = ["openalex", "scholar", "scienti", "minciencias", "ranking"]
            return hierarchy.index(title.source) if title.source in hierarchy else float("inf")
        first_title = sorted(work.titles, key=order)[0]
        work.language = first_title.lang
        work.title = first_title.title

    @staticmethod
    def set_product_types(work: Work):
        def order(product_type: ProductType):
            hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
            return hierarchy.index(product_type.source) if product_type.source in hierarchy else float("inf")

        product_types = list(map(
            lambda product_type: ProductType(name=product_type.type, source=product_type.source), work.types
        ))
        work.product_types = sorted(product_types, key=order)

    @staticmethod
    def set_bibliographic_info(work: Work):
        work.issue = work.bibliographic_info.issue
        work.open_access_status = work.bibliographic_info.open_access_status
        work.volume = work.bibliographic_info.volume
        work.bibliographic_info = None

    @staticmethod
    def set_authors_external_ids(work: Work):
        for author in work.authors:
            if author.id:
                author.external_ids = PersonRepository.get_person_by_id(str(author.id)).external_ids

    @staticmethod
    def limit_authors(work: Work, limit: int = 10):
        if len(work.authors) > limit:
            work.authors = work.authors[:limit]

    @staticmethod
    def set_external_ids(work: Work):
        new_external_ids = []
        for external_id in work.external_ids:
            if external_id.source in ["minciencias", "scienti"]:
                new_external_ids.append(external_id)
            else:
                work.external_urls.append(ExternalUrl(url=external_id.id, source=external_id.source))
        work.external_ids = list(set(new_external_ids))

    @staticmethod
    def set_external_urls(work: Work):
        new_external_urls = []
        for external_url in work.external_urls:
            url = str(external_url.url)
            if urlparse(url).scheme and urlparse(url).netloc:
                new_external_urls.append(external_url)
            else:
                if external_url.source in external_urls.keys() and url != "":
                    new_external_urls.append(ExternalUrl(
                        url=external_urls[external_url.source].format(id=url),
                        source=external_url.source
                    ))
        work.external_urls = list(set(new_external_urls))
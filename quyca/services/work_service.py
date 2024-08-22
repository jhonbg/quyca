from database.models.source_model import Source
from database.models.work_model import Work, Title, ProductType
from database.repositories.person_repository import PersonRepository
from database.repositories.source_repository import SourceRepository
from database.repositories.work_repository import WorkRepository


class WorkService:
    @classmethod
    def get_work_by_id(cls, work_id: str):
        work = WorkRepository.get_work_by_id(work_id)

        if work.authors:
            cls.limit_authors(work)
            cls.set_authors_external_ids(work)

        if work.bibliographic_info:
            cls.set_bibliographic_info(work)

        if work.source.id:
            source = SourceRepository.get_source_by_id(work.source.id)
            cls.set_source_serials(work, source)
            cls.set_source_scimago_quartile(work, source)

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
    def set_source_scimago_quartile(work: Work, source: Source):
        for ranking in source.ranking:
            condition = (
                    ranking.source == "scimago Best Quartile" and
                    ranking.rank is not "-" and
                    ranking.from_date <= work.date_published <= ranking.to_date
            )
            if condition:
                work.source.scimago_quartile = ranking.rank
                break

    @staticmethod
    def set_source_serials(work: Work, source: Source):
        serials = {}

        for external_id in source.external_ids:
            serials[external_id.source] = external_id.id

        work.source.serials = serials

    @staticmethod
    def limit_authors(work: Work, limit: int = 10):
        if len(work.authors) > limit:
            work.authors = work.authors[:limit]

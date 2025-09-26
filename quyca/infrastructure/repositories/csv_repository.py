from typing import Generator


from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.generators import work_generator
from quyca.infrastructure.mongo import database
from quyca.infrastructure.repositories import work_repository


def get_works_csv_by_person(person_id: str, query_params: QueryParams) -> Generator:
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "bibliographic_info": 1,
                "open_access": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
                "primary_topic": 1,
                "affiliations_data": {
                    "id": "$authors.affiliations.id",
                    "addresses": {"country": "$authors.affiliations.addresses.country"},
                    "ranking": "$authors.affiliations.ranking",
                },
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_affiliation(affiliation_id: str, query_params: QueryParams) -> Generator:
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "bibliographic_info": 1,
                "open_access": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
                "primary_topic": 1,
                "affiliations_data": {
                    "id": "$authors.affiliations.id",
                    "addresses": {"country": "$authors.affiliations.addresses.country"},
                    "ranking": "$authors.affiliations.ranking",
                },
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)

from typing import Generator

from bson import ObjectId

from infrastructure.generators import work_generator
from infrastructure.mongo import database


def get_works_csv_by_person(person_id: str) -> Generator:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "affiliations_data": 1,
                "bibliographic_info": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "source_data": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_csv_by_affiliation(affiliation_id: str) -> Generator:
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses.country": 1, "ranking": 1}}],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "external_urls": 1,
                            "ranking": 1,
                            "publisher": 1,
                            "apc": 1,
                        }
                    }
                ],
            }
        },
        {
            "$project": {
                "external_ids": 1,
                "authors": 1,
                "affiliations_data": 1,
                "bibliographic_info": 1,
                "citations_count": 1,
                "subjects": 1,
                "titles": 1,
                "types": 1,
                "source": 1,
                "source_data": 1,
                "year_published": 1,
                "ranking": 1,
                "abstract": 1,
            }
        },
    ]
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)

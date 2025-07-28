from infrastructure.mongo import database as db
from infrastructure.generators import news_generator
from infrastructure.repositories import base_repository
from typing import Generator
from domain.models.base_model import QueryParams


def cc_from_person(person_id: str) -> str | None:
    doc = db.person.find_one(
        {"_id": person_id, "external_ids.source": "Cédula de Ciudadanía"},
        {"external_ids.$": 1},
    )
    if doc and doc.get("external_ids"):
        return doc["external_ids"][0]["id"]
    return None


def get_news_by_person(person_id: str, query_params: QueryParams) -> Generator:
    cc = cc_from_person(person_id)
    if not cc:
        return iter([])

    page = query_params.page or 1
    limit = query_params.limit or 10
    skip = (page - 1) * limit

    pipeline = [
        {"$match": {"professor_id": cc}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$url_docs", {"medium": "$medium_docs.medium"}]}}},
        {"$skip": skip},
        {"$limit": limit},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    cursor = db.news_professors_collection.aggregate(pipeline, allowDiskUse=True)
    return news_generator.get(cursor)


def news_count_by_person(person_id: str) -> int:
    cc = cc_from_person(person_id)
    if not cc:
        return 0

    pipeline = [
        {"$match": {"professor_id": cc}},
        {"$unwind": "$classified_urls_ids"},
        {
            "$lookup": {
                "from": "news_urls_collection",
                "localField": "classified_urls_ids",
                "foreignField": "url_id",
                "as": "url_docs",
            }
        },
        {"$unwind": "$url_docs"},
        {
            "$lookup": {
                "from": "news_media_collection",
                "localField": "url_docs.medium_id",
                "foreignField": "medium_id",
                "as": "medium_docs",
            }
        },
        {"$unwind": "$medium_docs"},
        {"$count": "total"},
    ]
    result = list(db.news_professors_collection.aggregate(pipeline))
    return result[0]["total"] if result else 0

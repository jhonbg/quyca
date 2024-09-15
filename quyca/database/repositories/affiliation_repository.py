from typing import Generator

from bson import ObjectId

from database.models.base_model import QueryParams
from constants.institutions import institutions_list
from database.generators import affiliation_generator
from database.models.affiliation_model import Affiliation
from database.repositories import base_repository
from database.mongo import database
from database.repositories.base_repository import set_project
from exceptions.not_entity_exception import NotEntityException


def get_affiliation_by_id(affiliation_id: str) -> Affiliation:
    pipeline = [
        {"$match": {"_id": ObjectId(affiliation_id)}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "relations.id",
                "foreignField": "_id",
                "as": "relations_data",
                "pipeline": [{"$project": {"id": "$_id", "external_urls": 1}}],
            }
        },
    ]
    try:
        affiliation_data = database["affiliations"].aggregate(pipeline).next()
    except:
        raise NotEntityException(f"The affiliation with id {affiliation_id} does not exist.")
    return Affiliation(**affiliation_data)


def get_affiliations_by_institution(institution_id: str, relation_type: str) -> Generator:
    pipeline = [
        {
            "$match": {
                "relations.id": ObjectId(institution_id),
                "types.type": relation_type,
            }
        }
    ]
    set_project(pipeline, ["_id", "names"])
    affiliations = database["affiliations"].aggregate(pipeline)
    return affiliation_generator.get(affiliations)


def get_departments_by_faculty(faculty_id: str) -> Generator:
    return get_affiliations_by_institution(faculty_id, "department")


def get_groups_by_faculty_or_department(affiliation_id: str) -> Generator:
    institution_id = (
        database["affiliations"]
        .aggregate(
            [
                {"$match": {"_id": ObjectId(affiliation_id)}},
                {"$unwind": "$relations"},
                {"$match": {"relations.types.type": "education"}},
            ]
        )
        .next()
        .get("relations", [])["id"]
    )
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            }
        },
        {"$unwind": "$groups"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "groups.id",
                "foreignField": "_id",
                "as": "group",
                "pipeline": [
                    {
                        "$match": {
                            "relations.id": ObjectId(institution_id),
                            "types.type": "group",
                        },
                    },
                    {"$project": {"_id": 1}},
                ],
            }
        },
        {"$replaceRoot": {"newRoot": "$groups"}},
    ]
    groups = database["works"].aggregate(pipeline)
    return affiliation_generator.get(groups)


def get_related_affiliations_by_type(affiliation_id: str, affiliation_type: str, relation_type: str) -> Generator:
    pipeline = get_related_affiliations_by_type_pipeline(affiliation_id, affiliation_type, relation_type)
    if relation_type == "group" and affiliation_type in ["faculty", "department"]:
        collection = "person"
    else:
        collection = "affiliations"
    affiliations = database[collection].aggregate(pipeline)
    return affiliation_generator.get(affiliations)


def get_related_affiliations_by_type_pipeline(affiliation_id: str, affiliation_type: str, relation_type: str) -> list:
    if relation_type == "group":
        return get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)
    return [
        {
            "$match": {
                "relations.id": ObjectId(affiliation_id),
                "types.type": relation_type,
            }
        }
    ]


def search_affiliations(
    affiliation_type: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> (Generator, int):
    types = institutions_list if affiliation_type == "institution" else [affiliation_type]
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    pipeline += [
        {
            "$match": {
                "types.type": {"$in": types},
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$count": "count"}],
            }
        },
        {
            "$addFields": {
                "products_count": {"$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]},
            },
        },
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "relations.id",
                "foreignField": "_id",
                "as": "relations_data",
                "pipeline": [{"$project": {"id": "$_id", "external_urls": 1}}],
            }
        },
        {"$project": {"works": 0}},
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    affiliations = database["affiliations"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$match": {"types.type": {"$in": types}}},
        {"$count": "total_results"},
    ]
    total_results = next(database["affiliations"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return affiliation_generator.get(affiliations), total_results

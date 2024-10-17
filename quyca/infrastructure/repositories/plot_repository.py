from typing import Generator, Tuple

from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from infrastructure.generators import work_generator
from infrastructure.mongo import database, calculations_database


def get_affiliations_scienti_works_count_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$project": {"types": 1}}],
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {"$match": {"works.types.source": "scienti", "works.types.level": 2}},
        {
            "$group": {
                "_id": {"id": "$_id", "type": "$works.types.type", "name": "$names.name"},
                "works_count": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0, "type": "$_id.type", "works_count": 1, "name": {"$first": "$_id.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_scienti_works_count_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_scienti_works_count_by_institution(affiliation_id, "department")


def get_groups_scienti_works_count_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
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
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [{"$project": {"types": 1}}],
            }
        },
        {"$unwind": "$works"},
        {"$unwind": "$works.types"},
        {
            "$match": {
                "works.authors.affiliations.id": ObjectId(affiliation_id),
                "works.types.source": "scienti",
                "works.types.level": 2,
            }
        },
        {
            "$group": {
                "_id": {"id": "$_id", "type": "$works.types.type", "name": "$names.name"},
                "works_count": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0, "type": "$_id.type", "works_count": 1, "name": {"$first": "$_id.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_citations_count_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {"$project": {"_id": 0, "citations_count": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_citations_count_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_citations_count_by_institution(affiliation_id, "department")


def get_groups_citations_count_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
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
        .get("relations", {})
        .get("id", None)
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
                    {"$project": {"_id": 1, "name": {"$first": "$names.name"}, "citations_count": 1}},
                ],
            }
        },
        {"$unwind": "$group"},
        {"$replaceRoot": {"newRoot": "$group"}},
        {
            "$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "citations_count": {"$first": "$citations_count"},
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_affiliations_apc_expenses_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "work",
                "pipeline": [{"$project": {"source": 1}}],
            }
        },
        {"$unwind": "$work"},
        {
            "$lookup": {
                "from": "sources",
                "localField": "work.source.id",
                "foreignField": "_id",
                "as": "source",
                "pipeline": [{"$project": {"apc": 1}}],
            }
        },
        {"$unwind": "$source"},
        {"$project": {"_id": 0, "source": 1, "names": 1}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_apc_expenses_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_apc_expenses_by_institution(affiliation_id, "department")


def get_groups_apc_expenses_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
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
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "work",
                "pipeline": [
                    {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
                    {"$project": {"source": 1, "authors": 1}},
                ],
            }
        },
        {"$unwind": "$work"},
        {
            "$lookup": {
                "from": "sources",
                "localField": "work.source.id",
                "foreignField": "_id",
                "as": "source",
                "pipeline": [{"$project": {"apc": 1}}],
            }
        },
        {"$unwind": "$source"},
        {"$project": {"_id": 0, "source": 1, "names": 1}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_affiliations_works_citations_count_by_institution(institution_id: str, relation_type: str) -> CommandCursor:
    pipeline = [
        {"$match": {"relations.id": ObjectId(institution_id), "types.type": relation_type}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [
                    {
                        "$addFields": {
                            "scholar_citations_count": {
                                "$ifNull": [
                                    {
                                        "$arrayElemAt": [
                                            {
                                                "$map": {
                                                    "input": {
                                                        "$filter": {
                                                            "input": "$citations_count",
                                                            "as": "citation",
                                                            "cond": {
                                                                "$eq": [
                                                                    "$$citation.source",
                                                                    "scholar",
                                                                ]
                                                            },
                                                        }
                                                    },
                                                    "as": "filtered",
                                                    "in": "$$filtered.count",
                                                }
                                            },
                                            0,
                                        ]
                                    },
                                    0,
                                ]
                            }
                        }
                    },
                    {"$project": {"scholar_citations_count": 1}},
                ],
            }
        },
        {"$project": {"_id": 0, "works": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_departments_works_citations_count_by_faculty(affiliation_id: str) -> CommandCursor:
    return get_affiliations_works_citations_count_by_institution(affiliation_id, "department")


def get_groups_works_citations_count_by_faculty_or_department(affiliation_id: str) -> CommandCursor:
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
        .get("relations", {})
        .get("id", None)
    )
    pipeline = [
        {
            "$match": {
                "relations.id": institution_id,
                "types.type": "group",
            }
        },
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.affiliations.id",
                "as": "works",
                "pipeline": [
                    {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
                    {
                        "$addFields": {
                            "scholar_citations_count": {
                                "$ifNull": [
                                    {
                                        "$arrayElemAt": [
                                            {
                                                "$map": {
                                                    "input": {
                                                        "$filter": {
                                                            "input": "$citations_count",
                                                            "as": "citation",
                                                            "cond": {
                                                                "$eq": [
                                                                    "$$citation.source",
                                                                    "scholar",
                                                                ]
                                                            },
                                                        }
                                                    },
                                                    "as": "filtered",
                                                    "in": "$$filtered.count",
                                                }
                                            },
                                            0,
                                        ]
                                    },
                                    0,
                                ]
                            }
                        }
                    },
                    {"$project": {"scholar_citations_count": 1}},
                ],
            }
        },
        {"$project": {"_id": 0, "works": 1, "name": {"$first": "$names.name"}}},
    ]
    return database["affiliations"].aggregate(pipeline)


def get_active_authors_by_sex(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": ObjectId(affiliation_id), "end_date": -1}},
                "ranking.source": "staff",
            }
        },
        {"$project": {"_id": 0, "sex": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_active_authors_by_age_range(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {
            "$match": {
                "affiliations": {"$elemMatch": {"id": ObjectId(affiliation_id), "end_date": -1}},
                "ranking.source": "staff",
            }
        },
        {"$project": {"_id": 0, "birthdate": 1}},
    ]
    return database["person"].aggregate(pipeline)


def get_products_by_author_age_and_person(person_id: str) -> CommandCursor:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$project": {"authors": 1, "date_published": 1, "year_published": 1}},
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "pipeline": [{"$project": {"birthdate": 1}}],
                "as": "author",
            }
        },
        {"$unwind": "$author"},
        {
            "$project": {
                "work.date_published": "$date_published",
                "work.year_published": "$year_published",
                "birthdate": "$author.birthdate",
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_coauthorship_by_country_map_by_affiliation(affiliation_id: str) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {"$unwind": "$authors"},
        {"$unwind": "$authors.affiliations"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.country": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_country_map_by_person(person_id: str) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$unwind": "$authors"},
        {"$unwind": "$authors.affiliations"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.country": 1,
                        }
                    }
                ],
            }
        },
        {
            "$project": {
                "count": 1,
                "affiliation.addresses.country_code": 1,
                "affiliation.addresses.country": 1,
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_affiliation(affiliation_id: str) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {"$unwind": "$authors"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
                "pipeline": [
                    {
                        "$project": {
                            "addresses.country_code": 1,
                            "addresses.city": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_person(person_id: str) -> list:
    data = []
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$unwind": "$authors"},
        {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
        {"$unwind": "$_id"},
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "_id",
                "foreignField": "_id",
                "as": "affiliation",
            }
        },
        {
            "$project": {
                "count": 1,
                "affiliation.addresses.country_code": 1,
                "affiliation.addresses.city": 1,
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_collaboration_network(affiliation_id: str) -> CommandCursor:
    pipeline = [
        {"$match": {"_id": ObjectId(affiliation_id)}},
        {"$project": {"coauthorship_network": 1}},
        {
            "$lookup": {
                "from": "affiliations_edges",
                "localField": "_id",
                "foreignField": "_id",
                "as": "complement",
            }
        },
        {"$unwind": "$complement"},
        {
            "$project": {
                "coauthorship_network": {
                    "nodes": "$coauthorship_network.nodes",
                    "edges": {
                        "$concatArrays": [
                            "$coauthorship_network.edges",
                            "$complement.coauthorship_network.edges",
                        ]
                    },
                }
            }
        },
    ]
    return calculations_database["affiliations"].aggregate(pipeline)


def get_works_rankings_by_person(person_id: str) -> Tuple[Generator, int]:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {"$project": {"_id": 1, "ranking": 1}},
                ],
            }
        },
        {"$unwind": "$source_data"},
        {"$project": {"_id": 1, "source_data": 1, "date_published": 1}},
    ]
    count_pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$count": "total_results"},
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    works = database["works"].aggregate(pipeline)
    return work_generator.get(works), total_results


def get_products_by_database_by_affiliation(affiliation_id: str) -> dict:
    return {
        "minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                ]
            }
        ),
        "openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti_minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "minciencias_openalex_scholar_scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.affiliations.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
    }


def get_products_by_database_by_person(affiliation_id: str) -> dict:
    return {
        "minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                ]
            }
        ),
        "openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                ]
            }
        ),
        "minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "scienti_minciencias_openalex": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_minciencias_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "scienti_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
        "minciencias_openalex_scholar": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                ]
            }
        ),
        "minciencias_openalex_scholar_scienti": database["works"].count_documents(
            {
                "$and": [
                    {"authors.id": ObjectId(affiliation_id)},
                    {"updated.source": "minciencias"},
                    {"updated.source": "openalex"},
                    {"updated.source": "scholar"},
                    {"updated.source": "scienti"},
                ]
            }
        ),
    }

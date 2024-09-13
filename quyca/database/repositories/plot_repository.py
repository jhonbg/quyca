from bson import ObjectId

from database.generators import work_generator
from database.mongo import database, calculations_database


def get_bars_data_by_affiliation_type(
    affiliation_id: str, affiliation_type: str
) -> dict:
    pipeline = [
        {
            "$match": {
                "affiliations.types.type": affiliation_type,
                "affiliations.id": ObjectId(affiliation_id),
            }
        },
        {"$unwind": "$affiliations"},
        {"$match": {"affiliations.types.type": affiliation_type}},
        {"$project": {"authorIds": "$_id", "_id": 0, "affiliations": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "authorIds",
                "foreignField": "authors.id",
                "as": "works",
            }
        },
        {"$unwind": "$works"},
        {"$match": {"works.types": {"$ne": []}}},
        {
            "$project": {
                "name": "$affiliations.name",
                "work": {"types": "$works.types"},
            }
        },
    ]
    data = {}
    for _data in database["person"].aggregate(pipeline):
        if not data.get(_data["name"], False):
            data[_data["name"]] = []
        data[_data["name"]].append(_data["work"])
    return data


def get_bars_data_by_researcher_and_affiliation(
    affiliation_id, affiliation_type: str
) -> list:
    data = []
    if affiliation_type in ["group", "department", "faculty"]:
        for author in database["person"].find(
            {"affiliations.id": ObjectId(affiliation_id)}, {"affiliations": 1}
        ):
            pipeline = [
                {
                    "$match": {
                        "authors.id": author["_id"],
                        "year_published": {"$ne": None},
                    }
                },
                {"$project": {"year_published": 1, "authors": 1}},
                {"$unwind": "$authors"},
                {
                    "$lookup": {
                        "from": "person",
                        "localField": "authors.id",
                        "foreignField": "_id",
                        "as": "researcher",
                    }
                },
                {
                    "$project": {
                        "year_published": 1,
                        "researcher.ranking": 1,
                        "researcher._id": 1,
                    }
                },
                {"$match": {"researcher.ranking.source": "scienti"}},
            ]
            for work in database["works"].aggregate(pipeline):
                for researcher in work["researcher"]:
                    for rank in researcher["ranking"]:
                        if rank["source"] == "scienti":
                            data.append(
                                {
                                    "year_published": work["year_published"],
                                    "rank": rank["rank"],
                                }
                            )
    else:
        pipeline = [
            {
                "$match": {
                    "authors.affiliations.id": ObjectId(affiliation_id),
                    "year_published": {"$ne": None},
                }
            },
            {"$project": {"year_published": 1, "authors": 1}},
            {"$unwind": "$authors"},
            {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
            {
                "$lookup": {
                    "from": "person",
                    "localField": "authors.id",
                    "foreignField": "_id",
                    "as": "researcher",
                }
            },
            {"$project": {"year_published": 1, "researcher.ranking": 1}},
            {"$match": {"researcher.ranking.source": "scienti"}},
        ]
        for work in database["works"].aggregate(pipeline):
            for researcher in work["researcher"]:
                for rank in researcher["ranking"]:
                    if rank["source"] == "scienti":
                        data.append(
                            {
                                "year_published": work["year_published"],
                                "rank": rank["rank"],
                            }
                        )
    return data


def get_bars_data_by_researcher_and_person(person_id: str):
    data = []
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {"$project": {"year_published": 1, "authors": 1}},
        {"$unwind": "$authors"},
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "researcher",
            }
        },
        {"$project": {"year_published": 1, "researcher.ranking": 1}},
        {"$match": {"researcher.ranking.source": "scienti"}},
    ]
    for work in database["works"].aggregate(pipeline):
        for researcher in work["researcher"]:
            for rank in researcher["ranking"]:
                if rank["source"] == "scienti":
                    data.append(
                        {
                            "year_published": work["year_published"],
                            "rank": rank["rank"],
                        }
                    )
    return data


def get_products_by_author_sex(affiliation_id: str):
    pipeline = [
        {"$project": {"affiliations": 1, "sex": 1}},
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "work",
            }
        },
        {"$unwind": "$work"},
        {
            "$addFields": {
                "sex": {
                    "$cond": {
                        "if": {"$eq": ["$sex", ""]},
                        "then": "sin información",
                        "else": "$sex",
                    }
                }
            }
        },
        {"$project": {"sex": 1}},
        {"$group": {"_id": "$sex", "count": {"$sum": 1}}},
        {"$project": {"name": "$_id", "_id": 0, "value": "$count"}},
    ]
    return list(database["person"].aggregate(pipeline))


def get_products_by_author_age_and_affiliation(affiliation_id: str):
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "person",
                "pipeline": [
                    {
                        "$project": {
                            "birthdate": 1,
                            "affiliations": 1,
                        }
                    }
                ],
            }
        },
        {"$unwind": "$person"},
        {"$match": {"person.affiliations.id": ObjectId(affiliation_id)}},
        # {"$group": {"_id": "$_id", "document": {"$first": "$$ROOT"}}},
        # {"$replaceRoot": {"newRoot": "$document"}},
        {
            "$project": {
                "birthdate": "$person.birthdate",
                "work.date_published": "$date_published",
                "work.year_published": "$year_published",
            }
        },
    ]
    return database["works"].aggregate(pipeline)


def get_products_by_author_age_and_person(person_id: str):
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


def get_coauthorship_by_country_map_by_affiliation(affiliation_id, affiliation_type):
    data = []

    if affiliation_type in ["group", "department", "faculty"]:
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
            {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
            {"$project": {"_id": 1}},
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "authors.id",
                    "as": "work",
                    "pipeline": [{"$project": {"_id": 1, "authors": 1}}],
                }
            },
            {"$unwind": "$work"},
            {"$match": {"work.authors.affiliations.id": institution_id}},
            {"$unwind": "$work.authors"},
            {"$unwind": "$work.authors.affiliations"},
            {"$group": {"_id": "$work.authors.affiliations.id", "count": {"$sum": 1}}},
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

        for person in database["person"].aggregate(pipeline):
            data.append(person)
    else:
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


def get_coauthorship_by_country_map_by_person(person_id):
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
                "affiliation.addresses.country": 1,
            }
        },
        {"$unwind": "$affiliation"},
        {"$unwind": "$affiliation.addresses"},
    ]
    for work in database["works"].aggregate(pipeline):
        data.append(work)
    return data


def get_coauthorship_by_colombian_department_map_by_affiliation(
    affiliation_id, affiliation_type
):
    data = []
    if affiliation_type in ["group", "department", "faculty"]:
        for author in database["person"].find(
            {"affiliations.id": ObjectId(affiliation_id)}, {"affiliations": 1}
        ):
            pipeline = [
                {"$match": {"authors.id": author["_id"]}},
                {"$unwind": "$authors"},
                {
                    "$group": {
                        "_id": "$authors.affiliations.id",
                        "count": {"$sum": 1},
                    }
                },
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
    else:
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


def get_coauthorship_by_colombian_department_map_by_person(person_id: str):
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


def get_collaboration_network(affiliation_id):
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


def get_works_rankings_by_institution_or_group(affiliation_id: str):
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
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
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
        {"$count": "total_results"},
    ]
    total_results = next(
        database["works"].aggregate(count_pipeline), {"total_results": 0}
    )["total_results"]
    works = database["works"].aggregate(pipeline)
    return work_generator.get(works), total_results


def get_works_rankings_by_faculty_or_department(affiliation_id):
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
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "work",
            }
        },
        {"$unwind": "$work"},
        {"$match": {"work.authors.affiliations.id": institution_id}},
        {"$replaceRoot": {"newRoot": "$work"}},
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
        {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
        {"$project": {"_id": 1}},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "work",
            }
        },
        {"$unwind": "$work"},
        {"$match": {"work.authors.affiliations.id": institution_id}},
        {"$replaceRoot": {"newRoot": "$work"}},
        {"$count": "total_results"},
    ]
    total_results = next(
        database["person"].aggregate(count_pipeline), {"total_results": 0}
    )["total_results"]
    works = database["person"].aggregate(pipeline)
    return work_generator.get(works), total_results


def get_works_rankings_by_person(person_id: str):
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
    total_results = next(
        database["works"].aggregate(count_pipeline), {"total_results": 0}
    )["total_results"]
    works = database["works"].aggregate(pipeline)
    return work_generator.get(works), total_results

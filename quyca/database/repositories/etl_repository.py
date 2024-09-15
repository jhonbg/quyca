from database.mongo import database


def set_person_products_count():
    pipeline = [
        {"$match": {"products_count": {"$exists": False}}},
        {"$limit": 1000},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "works",
                "pipeline": [{"$count": "count"}],
            }
        },
        {"$addFields": {"products_count": {"$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]}}},
        {
            "$merge": {
                "into": "person",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    count_pipeline = [
        {"$match": {"products_count": {"$exists": False}}},
        {"$count": "total_results"},
    ]
    total_results = 1
    while total_results > 0:
        database["person"].aggregate(pipeline)
        total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)


def set_person_citations_count():
    pipeline = [
        {"$match": {"citations_count": {"$exists": False}}},
        {"$limit": 1000},
        {
            "$lookup": {
                "from": "works",
                "localField": "_id",
                "foreignField": "authors.id",
                "as": "works",
                "pipeline": [
                    {"$unwind": "$citations_count"},
                    {
                        "$group": {
                            "_id": "$_id",
                            "citations_count_openalex": {
                                "$sum": {
                                    "$cond": [
                                        {
                                            "$eq": [
                                                "$citations_count.source",
                                                "openalex",
                                            ]
                                        },
                                        "$citations_count.count",
                                        0,
                                    ]
                                }
                            },
                            "citations_count_scholar": {
                                "$sum": {
                                    "$cond": [
                                        {"$eq": ["$citations_count.source", "scholar"]},
                                        "$citations_count.count",
                                        0,
                                    ]
                                }
                            },
                        }
                    },
                ],
            }
        },
        {
            "$addFields": {
                "citations_count": [
                    {
                        "count": {
                            "$ifNull": [
                                {
                                    "$arrayElemAt": [
                                        "$works.citations_count_openalex",
                                        0,
                                    ]
                                },
                                0,
                            ]
                        },
                        "source": "openalex",
                    },
                    {
                        "count": {
                            "$ifNull": [
                                {"$arrayElemAt": ["$works.citations_count_scholar", 0]},
                                0,
                            ]
                        },
                        "source": "scholar",
                    },
                ],
            }
        },
        {
            "$merge": {
                "into": "person",
                "whenMatched": "merge",
                "whenNotMatched": "fail",
            }
        },
    ]
    count_pipeline = [
        {"$match": {"citations_count": {"$exists": False}}},
        {"$count": "total_results"},
    ]
    total_results = 1
    while total_results > 0:
        database["person"].aggregate(pipeline)
        total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)

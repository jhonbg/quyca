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
        {
            "$addFields": {
                "products_count": {
                    "$ifNull": [{"$arrayElemAt": ["$works.count", 0]}, 0]
                }
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
        {"$match": {"products_count": {"$exists": False}}},
        {"$count": "total_results"},
    ]
    total_results = 1
    while total_results > 0:
        database["person"].aggregate(pipeline)
        total_results = next(
            database["person"].aggregate(count_pipeline), {"total_results": 0}
        ).get("total_results", 0)

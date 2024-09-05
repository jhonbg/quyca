from database.models.base_model import QueryParams


def get_search_pipelines(
    query_params: QueryParams, pipeline_params: dict | None = None
):
    pipeline = [
        {"$match": {"$text": {"$search": query_params.keywords}}},
    ]
    count_pipeline = [
        {"$match": {"$text": {"$search": query_params.keywords}}},
        {"$count": "total_results"},
    ]
    process_params(pipeline, query_params, pipeline_params)
    return pipeline, count_pipeline


def process_params(
    pipeline, query_params: QueryParams, pipeline_params: dict | None = None
):
    if pipeline_params is None:
        pipeline_params = {}
    if match := pipeline_params.get("match"):
        pipeline += [{"$match": match}]
    if project := pipeline_params.get("project"):
        pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]
    if sort := query_params.sort:
        set_sort(sort, pipeline, query_params)

    if (page := query_params.page) and (limit := query_params.limit):
        skip = (page - 1) * limit
        pipeline += [{"$skip": skip}, {"$limit": limit}]


def set_sort(sort: str, pipeline: list, query_params: QueryParams):
    sort_field, direction = sort.split("_")
    direction = -1 if direction == "desc" else 1
    if sort_field == "citations":
        pipeline += [
            {
                "$addFields": {
                    "openalex_citations_count": {
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
                                                            "openalex",
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
            }
        ]
        sort_field = "openalex_citations_count"
    elif sort_field == "alphabetical":
        pipeline += [
            {
                "$addFields": {
                    "titles_order": {
                        "$map": {
                            "input": "$titles",
                            "as": "title",
                            "in": {
                                "source": "$$title.source",
                                "title": "$$title.title",
                                "order": {
                                    "$switch": {
                                        "branches": [
                                            {
                                                "case": {
                                                    "$eq": [
                                                        "$$title.source",
                                                        "openalex",
                                                    ]
                                                },
                                                "then": 0,
                                            },
                                            {
                                                "case": {
                                                    "$eq": ["$$title.source", "scholar"]
                                                },
                                                "then": 1,
                                            },
                                            {
                                                "case": {
                                                    "$eq": ["$$title.source", "scienti"]
                                                },
                                                "then": 2,
                                            },
                                            {
                                                "case": {
                                                    "$eq": [
                                                        "$$title.source",
                                                        "minciencias",
                                                    ]
                                                },
                                                "then": 3,
                                            },
                                            {
                                                "case": {
                                                    "$eq": ["$$title.source", "ranking"]
                                                },
                                                "then": 4,
                                            },
                                        ]
                                    }
                                },
                            },
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "first_title": {
                        "$arrayElemAt": [
                            {
                                "$sortArray": {
                                    "input": "$titles_order",
                                    "sortBy": {"order": 1},
                                }
                            },
                            0,
                        ]
                    }
                }
            },
            {"$addFields": {"title": "$first_title.title"}},
            {"$unset": ["titles_order", "first_title"]},
        ]
        sort_field = "title"
    elif sort_field == "products":
        sort_field = "products_count"
    elif sort_field == "year":
        sort_field = "year_published"
    pipeline += [{"$sort": {sort_field: direction}}]

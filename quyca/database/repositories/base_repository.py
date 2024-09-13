from database.models.base_model import QueryParams


def set_search_end_stages(
    pipeline: list, query_params: QueryParams, pipeline_params: dict = None
):
    if pipeline_params is None:
        pipeline_params = {}
    if sort := query_params.sort:
        set_sort(sort, pipeline)
    else:
        pipeline += [{"$sort": {"score": {"$meta": "textScore"}}}]
    set_project(pipeline, pipeline_params.get("project"))
    set_pagination(pipeline, query_params)
    return pipeline


def set_pagination(pipeline: list, query_params: QueryParams):
    if (page := query_params.page) and (limit := query_params.limit):
        skip = (page - 1) * limit
        pipeline += [{"$skip": skip}, {"$limit": limit}]


def set_match(pipeline: list, match: dict | None):
    if not match:
        return
    pipeline += [{"$match": match}]


def set_project(pipeline: list, project: list | None):
    if not project:
        return
    pipeline += [{"$project": {"_id": 1, **{p: 1 for p in project}}}]


def set_sort(sort: str | None, pipeline: list):
    if not sort:
        return
    sort_field, direction = sort.split("_")
    direction = -1 if direction == "desc" else 1
    if sort_field == "citations":
        pipeline += [
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
            }
        ]
        sort_field = "scholar_citations_count"
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

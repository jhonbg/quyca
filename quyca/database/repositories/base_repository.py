from database.models.base_model import QueryParams


def get_search_pipelines(
    query_params: QueryParams, pipeline_params: dict | None = None
):
    pipeline = [
        {"$match": {"$text": {"$search": query_params.keywords}}},
        {"$sort": {"score": {"$meta": "textScore"}}},
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
    if limit := query_params.limit:
        pipeline += [{"$limit": limit}]
    if page := query_params.page:
        skip = (page - 1) * limit
        pipeline += [{"$skip": skip}]

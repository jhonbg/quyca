from typing import Generator, Tuple

from bson import ObjectId

from quyca.infrastructure.generators import work_generator
from quyca.domain.models.base_model import QueryParams
from quyca.domain.models.work_model import Work
from quyca.infrastructure.repositories import base_repository
from quyca.infrastructure.mongo import database
from quyca.domain.exceptions.not_entity_exception import NotEntityException


def get_work_by_id(work_id: str) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise NotEntityException(f"The work with id {work_id} does not exist.")
    return Work(**work)


def get_works_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_with_source_by_affiliation(
    affiliation_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_affiliation(affiliation_id: str, query_params: QueryParams) -> int:
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    set_product_filters(pipeline, query_params)
    pipeline += [{"$count": "total"}]
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_works_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_with_source_by_person(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    set_product_filters(pipeline, query_params)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_count_by_person(person_id: str, query_params: QueryParams) -> int:
    pipeline = [{"$match": {"authors.id": person_id}}]
    set_product_filters(pipeline, query_params)
    pipeline += [{"$count": "total"}]
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_works(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_filters(pipeline, query_params)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    works = database["works"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_filters(count_pipeline, query_params)
    count_pipeline += [
        {"$count": "total_results"},
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return work_generator.get(works), total_results


def get_works_available_filters_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_works_available_filters_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_search_works_available_filters(query_params: QueryParams, pipeline_params: dict | None = None) -> dict:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    return get_works_available_filters(pipeline, query_params)


def get_works_available_filters(pipeline: list, query_params: QueryParams) -> dict:
    """
    This function builds and execute an aggregation pipeline to retrieve available filters.

    Parameters
    ----------
    pipeline: list
        List of agregation stages to filter the works before calculating available filters.
    query_params: QueryParams
        Query parameters containing the filters to apply.

    Returns
    -------
    available_filters: dict
        A dictionary with the different categories of available filters,
        each one computed using a `$facet` stage in the aggregation:
    """
    set_product_filters(pipeline, query_params)
    facet_stage = {
        "$facet": {
            "product_types": [
                {"$unwind": "$types"},
                {"$project": {"types.provenance": 0}},
                {"$group": {"_id": "types.source", "types": {"$addToSet": "$types"}}},
            ],
            "years": [
                {"$match": {"year_published": {"$type": "number"}}},
                {
                    "$group": {
                        "_id": None,
                        "min_year": {"$min": "$year_published"},
                        "max_year": {"$max": "$year_published"},
                    }
                },
                {"$project": {"_id": 0, "min_year": 1, "max_year": 1}},
            ],
            "status": [
                {"$group": {"_id": "$open_access.open_access_status"}},
            ],
            "subjects": [
                {"$unwind": "$subjects"},
                {"$unwind": "$subjects.subjects"},
                {"$match": {"subjects.subjects.level": {"$in": [0, 1]}}},
                {"$group": {"_id": "$subjects.source", "subjects": {"$addToSet": "$subjects.subjects"}}},
            ],
            "countries": [
                {"$unwind": "$authors"},
                {"$unwind": "$authors.affiliations"},
                {"$group": {"_id": "$authors.affiliations.country_code"}},
            ],
            "groups_ranking": [
                {"$unwind": "$groups"},
                {"$group": {"_id": "$groups.ranking"}},
            ],
            "authors_ranking": [
                {"$unwind": "$authors"},
                {"$group": {"_id": "$authors.ranking"}},
            ],
            "topics": [
                {"$match": {"primary_topic": {"$ne": {}}}},
                {
                    "$group": {
                        "_id": {"id": "$primary_topic.id", "display_name": "$primary_topic.display_name"},
                        "count": {"$sum": 1},
                    }
                },
                {"$project": {"_id": 0, "id": "$_id.id", "display_name": "$_id.display_name", "count": 1}},
                {"$sort": {"count": -1}},
            ],
        }
    }

    results = list(database["works"].aggregate(pipeline + [facet_stage]))[0]

    available_filters = {
        "product_types": results.get("product_types", []),
        "years": results.get("years", [{}])[0] if results.get("years") else {"min_year": None, "max_year": None},
        "status": results.get("status", []),
        "subjects": results.get("subjects", []),
        "countries": results.get("countries", []),
        "groups_ranking": results.get("groups_ranking", []),
        "authors_ranking": results.get("authors_ranking", []),
        "topics": results.get("topics", []),
    }

    return available_filters


def set_product_filters(pipeline: list, query_params: QueryParams) -> None:
    set_product_type_filters(pipeline, query_params.product_types)
    set_year_filters(pipeline, query_params.years)
    set_status_filters(pipeline, query_params.status)
    set_subject_filters(pipeline, query_params.subjects)
    set_topic_filters(pipeline, query_params.topics)
    set_country_filters(pipeline, query_params.countries)
    set_groups_ranking_filters(pipeline, query_params.groups_ranking)
    set_authors_ranking_filters(pipeline, query_params.authors_ranking)


def set_product_type_filters(pipeline: list, type_filters: str | None) -> None:
    if not type_filters:
        return
    match_filters = []
    for type_filter in type_filters.split(","):
        params = type_filter.split("_")
        if len(params) == 1:
            match_filters.append({"types": {"$elemMatch": {"source": params[0]}}})
        elif len(params) == 2:
            match_filters.append({"types": {"$elemMatch": {"source": params[0], "type": params[1]}}})
        elif len(params) == 3 and params[0] == "scienti":
            match_filters.append(
                {"types": {"$elemMatch": {"source": params[0], "type": params[1], "code": {"$regex": "^" + params[2]}}}}
            )
    pipeline += [{"$match": {"$or": match_filters}}]


def set_year_filters(pipeline: list, years: str | None) -> None:
    if not years:
        return
    year_list = [int(year) for year in years.split(",")]
    first_year = min(year_list)
    last_year = max(year_list)
    pipeline += [{"$match": {"year_published": {"$gte": first_year, "$lte": last_year}}}]


def set_status_filters(pipeline: list, status: str | None) -> None:
    if not status:
        return
    match_filters = []
    for single_status in status.split(","):
        if single_status == "unknown":
            match_filters.append({"open_access.open_access_status": None})
        elif single_status == "open":
            match_filters.append({"open_access.open_access_status": {"$nin": [None, "closed"]}})
        else:
            match_filters.append({"open_access.open_access_status": single_status})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_subject_filters(pipeline: list, subjects: str | None) -> None:
    if not subjects:
        return
    match_filters = []
    for subject in subjects.split(","):
        params = subject.split("_")
        if len(params) == 1:
            return
        match_filters.append({"subjects.subjects": {"$elemMatch": {"level": int(params[0]), "name": params[1]}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_topic_filters(pipeline: list, topics: str | None) -> None:
    if not topics:
        return
    match_filters = []
    for topic in topics.split(","):
        match_filters.append(topic.strip())
    pipeline += [{"$match": {"primary_topic.id": {"$in": match_filters}}}]


def set_country_filters(pipeline: list, countries: str | None) -> None:
    if not countries:
        return
    match_filters = []
    for country in countries.split(","):
        match_filters.append({"authors.affiliations": {"$elemMatch": {"country_code": country}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_groups_ranking_filters(pipeline: list, groups_ranking: str | None) -> None:
    if not groups_ranking:
        return
    match_filters = []
    for ranking in groups_ranking.split(","):
        match_filters.append({"groups": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]


def set_authors_ranking_filters(pipeline: list, authors_ranking: str | None) -> None:
    if not authors_ranking:
        return
    match_filters = []
    for ranking in authors_ranking.split(","):
        match_filters.append({"authors": {"$elemMatch": {"ranking": ranking}}})
    pipeline += [{"$match": {"$or": match_filters}}]

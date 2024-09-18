from itertools import chain

from bson import ObjectId

from database.models.base_model import QueryParams
from database.mongo import calculations_database, database
from database.repositories import plot_repository, work_repository
from services.parsers import map_parser, pie_parser, bar_parser


def get_person_plot(person_id: str, query_params: QueryParams) -> dict:
    return globals()["plot_" + query_params.plot](person_id, query_params)


def plot_annual_evolution_by_scienti_classification(person_id: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_person(person_id, query_params)
    return {"plot": bar_parser.parse_annual_evolution_by_scienti_classification(works)}


def plot_annual_citation_count(person_id: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_person(person_id, query_params)
    return {"plot": bar_parser.parse_annual_citation_count(works)}


def plot_annual_apc_expenses(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {
            "$and": [
                {"apc.charges": {"$exists": 1}},
                {"apc.currency": {"$exists": 1}},
            ]
        },
        "project": ["apc"],
    }
    sources = work_repository.get_sources_by_person(person_id, query_params, pipeline_params)
    return {"plot": bar_parser.apc_by_year(sources, 2022)}


def plot_annual_articles_open_access(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {
            "bibliographic_info.is_open_access": {"$ne": None},
            "year_published": {"$ne": None},
        },
        "project": ["year_published", "bibliographic_info"],
    }
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    return {"plot": bar_parser.parse_annual_articles_open_access(works)}


def plot_annual_articles_by_top_publishers(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
        "project": ["publisher", "apc"],
    }
    sources = work_repository.get_sources_by_person(person_id, query_params, pipeline_params)
    return {"plot": bar_parser.works_by_publisher_year(sources)}


def plot_most_used_title_words(person_id: str, query_params: QueryParams) -> dict:
    data = calculations_database["person"].find_one({"_id": ObjectId(person_id)}, {"top_words": 1})
    if data:
        if not "top_words" in data.keys():
            return {"plot": None}
        data = data["top_words"]
        if not data:
            return {
                "plot": [{"name": "Sin información", "value": 1, "percentage": 100}],
                "sum": 1,
            }
        return {"plot": data}
    else:
        return {"plot": None}


def plot_articles_by_publisher(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_person(person_id, query_params, pipeline_params)
    data = map(lambda x: x.publisher.name, sources)
    return pie_parser.get_products_by_publisher(data)


def plot_products_by_subject(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"subjects": {"$ne": []}},
        "project": ["subjects"],
    }
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    data = chain.from_iterable(
        map(
            lambda x: [sub for subject in x.subjects for sub in subject.subjects if subject.source == "openalex"],
            works,
        )
    )
    return pie_parser.get_products_by_subject(data)


def plot_products_by_database(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"updated": {"$ne": []}},
        "project": ["updated"],
    }
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    data = chain.from_iterable(map(lambda x: x.updated, works))
    return pie_parser.get_products_by_database(data)


def plot_articles_by_access_route(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"bibliographic_info.open_access_status": {"$exists": 1}},
        "project": ["bibliographic_info"],
    }
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    data = map(lambda x: x.bibliographic_info.open_access_status, works)
    return pie_parser.get_products_by_open_access(data)


def plot_products_by_author_age_range(person_id: str, query_params: QueryParams) -> dict:
    works = plot_repository.get_products_by_author_age_and_person(person_id)
    result = pie_parser.get_products_by_age(works)
    if result:
        return result
    else:
        return {"plot": None}


def plot_articles_by_scienti_category(person_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"ranking": {"$ne": []}},
        "project": ["ranking"],
    }
    works = work_repository.get_works_by_person(person_id, query_params, pipeline_params)
    data = chain.from_iterable(map(lambda x: x.ranking, works))
    return pie_parser.get_articles_by_scienti_category(data)


def plot_articles_by_scimago_quartile(person_id: str, query_params: QueryParams) -> dict:
    works, total_results = plot_repository.get_works_rankings_by_person(person_id)
    data = []
    works_data = []
    for work in works:
        for ranking in work.source_data.ranking:
            condition = (
                ranking.source in ["Scimago Best Quartile", "scimago Best Quartile"]
                and ranking.rank != "-"
                and work.date_published
                and ranking.from_date <= work.date_published <= ranking.to_date
            )
            if condition:
                data.append(ranking.rank)
                break
        works_data.append(work)
    return pie_parser.get_articles_by_scimago_quartile(data, total_results)


def plot_articles_by_publishing_institution(person_id: str, query_params: QueryParams) -> dict:
    person = database["person"].find_one({"_id": ObjectId(person_id)}, {"affiliations": 1})
    institution_id = None
    found = False
    for affiliation in person["affiliations"]:
        if found:
            break
        for type in affiliation["types"]:
            if not type["type"] in ["faculty", "department", "group"]:
                institution_id = affiliation["id"]
                found = True
                break
    institution = database["affiliations"].find_one({"_id": ObjectId(institution_id)}, {"names": 1})
    pipeline_params = {
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_person(person_id, query_params, pipeline_params)
    return pie_parser.get_products_by_same_institution(sources, institution)


def plot_coauthorship_by_country_map(person_id: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_coauthorship_by_country_map_by_person(person_id)
    result = map_parser.get_coauthorship_by_country_map(data)
    if result:
        return {"plot": result}
    else:
        return {"plot": None}


def plot_coauthorship_by_colombian_department_map(person_id: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_coauthorship_by_colombian_department_map_by_person(person_id)
    return {"plot": map_parser.get_coauthorship_by_colombian_department_map(data)}


def plot_author_coauthorship_network(person_id: str, query_params: QueryParams) -> dict:
    data = calculations_database["person"].find_one({"_id": ObjectId(person_id)}, {"coauthorship_network": 1})
    if data:
        if "coauthorship_network" not in data.keys():
            return {"plot": None}
        data = data["coauthorship_network"]
        nodes = sorted(data["nodes"], key=lambda x: x["degree"], reverse=True)[:50]
        nodes_ids = [node["id"] for node in nodes]
        edges = []
        for edge in data["edges"]:
            if edge["source"] in nodes_ids and edge["target"] in nodes_ids:
                edges.append(edge)
        return {"plot": {"nodes": nodes, "edges": edges}}
    else:
        return {"plot": None}

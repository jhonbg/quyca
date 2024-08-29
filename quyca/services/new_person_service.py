from itertools import chain

from bson import ObjectId
from werkzeug.datastructures.structures import MultiDict

from services.parsers import work_parser
from services import new_source_service
from services.parsers import bar_parser
from services.parsers import map_parser
from services.parsers import pie_parser
from database.models.person_model import Person
from database.mongo import calculations_database, database
from database.repositories import calculations_repository
from database.repositories import person_repository
from database.repositories import plot_repository
from database.repositories import work_repository


def get_person_by_id(person_id: str) -> Person:
    person = person_repository.get_person_by_id(person_id)
    person_calculations = calculations_repository.get_person_calculations(person_id)
    person.citations_count = person_calculations.citations_count
    person.products_count = work_repository.get_works_count_by_person(person_id)
    return person


def get_person_plot(person_id: str, query_params: MultiDict):
    return globals()["plot_" + query_params.get("plot")](person_id, query_params)


def plot_year_type(person_id: str, query_params):
    works = work_repository.get_works_by_person(person_id, query_params)
    return {"plot": bar_parser.get_by_work_year_and_work_type(works)}


def plot_year_citations(person_id: str, query_params):
    works = work_repository.get_works_by_person(person_id, query_params)
    return {"plot": bar_parser.get_citations_by_year(works)}


def plot_year_apc(person_id: str, query_params):
    pipeline_params = {
        "match": {
            "$and": [
                {"apc.charges": {"$exists": 1}},
                {"apc.currency": {"$exists": 1}},
            ]
        },
        "project": ["apc"],
    }
    sources = work_repository.get_sources_by_person(
        person_id, query_params, pipeline_params
    )
    return {"plot": bar_parser.apc_by_year(sources, 2022)}


def plot_year_oa(person_id: str, query_params):
    pipeline_params = {
        "match": {
            "bibliographic_info.is_open_access": {"$ne": None},
            "year_published": {"$ne": None},
        },
        "project": ["year_published", "bibliographic_info"],
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    return {"plot": bar_parser.oa_by_year(works)}


def plot_year_publisher(person_id: str, query_params):
    pipeline_params = {
        "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
        "project": ["publisher", "apc"],
    }
    sources = work_repository.get_sources_by_person(
        person_id, query_params, pipeline_params
    )
    return {"plot": bar_parser.works_by_publisher_year(sources)}


def plot_year_h(person_id: str, query_params):
    pipeline_params = {
        "match": {"citations_by_year": {"$exists": 1}},
        "project": {"citations_by_year"},
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    return {"plot": bar_parser.h_index_by_year(works)}


def plot_year_researcher(person_id: str, query_params):
    data = plot_repository.get_bars_data_by_researcher_and_person(person_id)
    plot = bar_parser.works_by_researcher_category_and_year(data)
    if plot:
        return {"plot": plot}
    else:
        return {"plot": None}


def plot_title_words(person_id: str, query_params):
    data = calculations_database["person"].find_one(
        {"_id": ObjectId(person_id)}, {"top_words": 1}
    )
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


def plot_products_publisher(person_id: str, query_params):
    pipeline_params = {
        "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_person(
        person_id, query_params, pipeline_params
    )
    data = map(lambda x: x.publisher.name, sources)
    return pie_parser.get_products_by_publisher(data)


def plot_products_subject(person_id: str, query_params):
    pipeline_params = {
        "match": {"subjects": {"$ne": []}},
        "project": ["subjects"],
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    data = chain.from_iterable(
        map(
            lambda x: [
                sub
                for subject in x.subjects
                for sub in subject.subjects
                if subject.source == "openalex"
            ],
            works,
        )
    )
    return pie_parser.get_products_by_subject(data)


def plot_products_database(person_id: str, query_params):
    pipeline_params = {
        "match": {"updated": {"$ne": []}},
        "project": ["updated"],
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    data = chain.from_iterable(map(lambda x: x.updated, works))
    return pie_parser.get_products_by_database(data)


def plot_products_oa(person_id: str, query_params):
    pipeline_params = {
        "match": {"bibliographic_info.open_access_status": {"$exists": 1}},
        "project": ["bibliographic_info"],
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    data = map(lambda x: x.bibliographic_info.open_access_status, works)
    return pie_parser.get_products_by_open_access(data)


def plot_products_age(person_id: str, query_params):
    works = plot_repository.get_products_by_author_age_and_person(person_id)
    result = pie_parser.get_products_by_age(works)
    if result:
        return result
    else:
        return {"plot": None}


def plot_scienti_rank(person_id: str, query_params):
    pipeline_params = {
        "match": {"ranking": {"$ne": []}},
        "project": ["ranking"],
    }
    works = work_repository.get_works_by_person(
        person_id, query_params, pipeline_params
    )
    data = chain.from_iterable(map(lambda x: x.ranking, works))
    return pie_parser.get_products_by_scienti_rank(data)


def plot_scimago_rank(person_id: str, query_params):
    pipeline_params = {
        "project": ["ranking"],
    }
    sources = work_repository.get_sources_by_person(
        person_id, query_params, pipeline_params
    )
    data = chain.from_iterable(map(lambda x: x.ranking, sources))
    return pie_parser.get_products_by_scimago_rank(data)


def plot_published_institution(person_id: str, query_params):
    person = database["person"].find_one(
        {"_id": ObjectId(person_id)}, {"affiliations": 1}
    )
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
    institution = database["affiliations"].find_one(
        {"_id": ObjectId(institution_id)}, {"names": 1}
    )
    pipeline_params = {
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_person(
        person_id, query_params, pipeline_params
    )
    return pie_parser.get_products_by_same_institution(sources, institution)


def plot_collaboration_worldmap(person_id: str, query_params):
    data = plot_repository.get_collaboration_worldmap_by_person(person_id)
    result = map_parser.get_collaboration_worldmap(data)
    if result:
        return {"plot": result}
    else:
        return {"plot": None}


def plot_collaboration_colombiamap(person_id: str, query_params):
    data = plot_repository.get_collaboration_colombiamap_by_person(person_id)
    return {"plot": map_parser.get_collaboration_colombiamap(data)}


def plot_collaboration_network(person_id: str, query_params):
    data = calculations_database["person"].find_one(
        {"_id": ObjectId(person_id)}, {"coauthorship_network": 1}
    )
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

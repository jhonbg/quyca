from itertools import chain

from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from database.models.base_model import QueryParams
from database.mongo import calculations_database, database
from database.repositories import work_repository, plot_repository
from services.parsers import bar_parser, pie_parser, map_parser


def get_affiliation_plot(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict | None:
    plot_type = query_params.plot
    plot_type_dict = {
        "faculties_by_product_type": "faculty",
        "departments_by_product_type": "department",
        "research_groups_by_product_type": "group",
    }
    if plot_type in plot_type_dict.keys():
        relation_type = plot_type_dict[plot_type]
        return plot_affiliations_by_product_type(affiliation_id, affiliation_type, relation_type)
    if plot_type in [
        "citations_by_faculty",
        "citations_by_department",
        "citations_by_research_group",
    ]:
        relation_type = plot_type.split("_")[-1]
        return plot_citations_by_affiliations(affiliation_id, affiliation_type, relation_type)
    if plot_type in [
        "apc_expenses_by_faculty",
        "apc_expenses_by_department",
        "apc_expenses_by_group",
    ]:
        relation_type = plot_type.split("_")[-1]
        return plot_apc_expenses_by_affiliation(affiliation_id, affiliation_type, relation_type)
    if plot_type in [
        "h_index_by_faculty",
        "h_index_by_department",
        "h_index_by_research_group",
    ]:
        relation_type = plot_type.split("_")[-1]
        return plot_h_index_by_affiliation(affiliation_id, affiliation_type, relation_type, query_params)
    return globals()["plot_" + plot_type](affiliation_id, affiliation_type, query_params)


def plot_affiliations_by_product_type(
    affiliation_id: str,
    affiliation_type: str,
    relation_type: str,
) -> dict | None:
    data: CommandCursor | None = None
    if affiliation_type == "institution":
        data = plot_repository.get_affiliations_scienti_works_count_by_institution(affiliation_id, relation_type)
    elif affiliation_type == "faculty" and relation_type == "department":
        data = plot_repository.get_departments_scienti_works_count_by_faculty(affiliation_id)
    elif affiliation_type in ["faculty", "department"] and relation_type == "group":
        data = plot_repository.get_groups_scienti_works_count_by_faculty_or_department(affiliation_id)
    return {"plot": bar_parser.parse_affiliations_by_product_type(data)}


def plot_citations_by_affiliations(affiliation_id: str, affiliation_type: str, relation_type: str) -> dict:
    data: CommandCursor | None = None
    if affiliation_type == "institution":
        data = plot_repository.get_affiliations_citations_count_by_institution(affiliation_id, relation_type)
    elif affiliation_type == "faculty" and relation_type == "department":
        data = plot_repository.get_departments_citations_count_by_faculty(affiliation_id)
    elif affiliation_type in ["faculty", "department"] and relation_type == "group":
        data = plot_repository.get_groups_citations_count_by_faculty_or_department(affiliation_id)
    return pie_parser.parse_citations_by_affiliations(data)


def plot_apc_expenses_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str) -> dict:
    data = plot_repository.get_affiliations_apc_expenses_by_institution(affiliation_id, relation_type)
    return pie_parser.parse_apc_expenses_by_affiliations(data, 2022)


def plot_h_index_by_affiliation(
    affiliation_id: str, affiliation_type: str, relation_type: str, query_params: QueryParams
) -> dict:
    data: CommandCursor | None = None
    if affiliation_type == "institution":
        data = plot_repository.get_affiliations_works_citations_count_by_institution(affiliation_id, relation_type)
    elif affiliation_type == "faculty" and relation_type == "department":
        data = plot_repository.get_departments_works_citations_count_by_faculty(affiliation_id)
    elif affiliation_type in ["faculty", "department"] and relation_type == "group":
        data = plot_repository.get_groups_works_citations_count_by_faculty_or_department(affiliation_id)
    return pie_parser.parse_h_index_by_affiliation(data)


def plot_annual_evolution_by_scienti_classification(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict:
    pipeline_params = {"project": ["year_published", "types"]}
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return {"plot": bar_parser.parse_annual_evolution_by_scienti_classification(works)}


def plot_annual_citation_count(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params)
    return {"plot": bar_parser.get_citations_by_year(works)}


def plot_annual_apc_expenses(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {
            "$and": [
                {"apc.charges": {"$exists": 1}},
                {"apc.currency": {"$exists": 1}},
            ]
        },
        "project": ["apc"],
    }
    sources = work_repository.get_sources_by_affiliation(affiliation_id, pipeline_params)
    return {"plot": bar_parser.apc_by_year(sources, 2022)}


def plot_annual_articles_open_access(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {
            "bibliographic_info.is_open_access": {"$ne": None},
            "year_published": {"$ne": None},
        },
        "project": ["year_published", "bibliographic_info"],
    }
    works = work_repository.get_works_by_affiliation(
        affiliation_id,
        query_params,
        pipeline_params,
    )
    return {"plot": bar_parser.oa_by_year(works)}


def plot_annual_articles_by_top_publishers(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict:
    pipeline_params = {
        "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
        "project": ["publisher", "apc"],
    }
    sources = work_repository.get_sources_by_affiliation(affiliation_id, pipeline_params)
    return {"plot": bar_parser.works_by_publisher_year(sources)}


def plot_most_used_title_words(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    data = calculations_database["affiliations"].find_one({"_id": ObjectId(affiliation_id)}, {"top_words": 1})
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


def plot_articles_by_publisher(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_affiliation(affiliation_id, pipeline_params)
    data = map(
        lambda x: (x.publisher.name if x.publisher and isinstance(x.publisher.name, str) else "Sin información"),
        sources,
    )
    return pie_parser.get_products_by_publisher(data)


def plot_products_by_subject(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"subjects": {"$ne": []}},
        "project": ["subjects"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    data = chain.from_iterable(
        map(
            lambda x: [sub for subject in x.subjects for sub in subject.subjects if subject.source == "openalex"],
            works,
        )
    )
    return pie_parser.get_products_by_subject(data)


def plot_products_by_database(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"updated": {"$ne": []}},
        "project": ["updated"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    data = chain.from_iterable(map(lambda x: x.updated, works))
    return pie_parser.get_products_by_database(data)


def plot_articles_by_access_route(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": ["bibliographic_info"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    data = map(
        lambda x: (
            x.bibliographic_info.open_access_status if x.bibliographic_info.open_access_status else "Sin información"
        ),
        works,
    )
    return pie_parser.get_products_by_open_access(data)


@pie_parser.get_percentage
def plot_products_by_author_sex(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> list:
    return plot_repository.get_products_by_author_sex(affiliation_id)


def plot_products_by_author_age_range(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    works = plot_repository.get_products_by_author_age_and_affiliation(affiliation_id)
    result = pie_parser.get_products_by_age(works)
    if result:
        return result
    else:
        return {"plot": None}


def plot_articles_by_scienti_category(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"ranking": {"$ne": []}},
        "project": ["ranking"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    total_works = work_repository.get_works_count_by_affiliation(affiliation_id)
    data = chain.from_iterable(map(lambda x: x.ranking, works))
    return pie_parser.get_articles_by_scienti_category(data, total_works)


def plot_articles_by_scimago_quartile(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict | None:
    works = None
    total_results = 0
    if affiliation_type in ["institution", "group"]:
        (
            works,
            total_results,
        ) = plot_repository.get_works_rankings_by_institution_or_group(affiliation_id)
    elif affiliation_type in ["faculty", "department"]:
        (
            works,
            total_results,
        ) = plot_repository.get_works_rankings_by_faculty_or_department(affiliation_id)
    data = []
    works_data = []
    if not works:
        return None
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


def plot_articles_by_publishing_institution(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict:
    institution = database["affiliations"].find_one({"_id": ObjectId(affiliation_id)}, {"names": 1})
    pipeline_params = {
        "project": ["publisher"],
    }
    sources = work_repository.get_sources_by_affiliation(affiliation_id, pipeline_params)
    return pie_parser.get_products_by_same_institution(sources, institution)


def plot_coauthorship_by_country_map(affiliation_id: str, affiliation_type: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_coauthorship_by_country_map_by_affiliation(affiliation_id, affiliation_type)
    result = map_parser.get_coauthorship_by_country_map(data)
    if result:
        return {"plot": result}
    else:
        return {"plot": None}


def plot_coauthorship_by_colombian_department_map(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict:
    data = plot_repository.get_coauthorship_by_colombian_department_map_by_affiliation(affiliation_id, affiliation_type)
    return {"plot": map_parser.get_coauthorship_by_colombian_department_map(data)}


def plot_institutional_coauthorship_network(
    affiliation_id: str, affiliation_type: str, query_params: QueryParams
) -> dict:
    if affiliation_type in ["group", "department", "faculty"]:
        return {"plot": None}
    data = calculations_database["affiliations"].find_one(
        {"_id": ObjectId(affiliation_id)}, {"coauthorship_network": 1}
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

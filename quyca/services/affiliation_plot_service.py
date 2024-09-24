from bson import ObjectId
from pymongo.command_cursor import CommandCursor

from database.models.base_model import QueryParams
from database.mongo import calculations_database, database
from database.repositories import work_repository, plot_repository, calculations_repository
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
        return plot_h_index_by_affiliation(affiliation_id, affiliation_type, relation_type)
    return globals()["plot_" + plot_type](affiliation_id, query_params)


def plot_affiliations_by_product_type(affiliation_id: str, affiliation_type: str, relation_type: str) -> dict | None:
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


def plot_h_index_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str) -> dict:
    data: CommandCursor | None = None
    if affiliation_type == "institution":
        data = plot_repository.get_affiliations_works_citations_count_by_institution(affiliation_id, relation_type)
    elif affiliation_type == "faculty" and relation_type == "department":
        data = plot_repository.get_departments_works_citations_count_by_faculty(affiliation_id)
    elif affiliation_type in ["faculty", "department"] and relation_type == "group":
        data = plot_repository.get_groups_works_citations_count_by_faculty_or_department(affiliation_id)
    return pie_parser.parse_h_index_by_affiliation(data)


def plot_annual_evolution_by_scienti_classification(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {"project": ["year_published", "types"]}
    works = work_repository.get_works_by_affiliation(affiliation_id, QueryParams(), pipeline_params)
    return {"plot": bar_parser.parse_annual_evolution_by_scienti_classification(works)}


def plot_annual_citation_count(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": ["citations_by_year"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return bar_parser.parse_annual_citation_count(works)


def plot_annual_articles_open_access(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": ["year_published", "bibliographic_info.is_open_access"],
        "match": {"types.source": "scienti", "types.level": 2},
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return bar_parser.parse_annual_articles_open_access(works)


def plot_annual_articles_by_top_publishers(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "source_project": ["publisher", "apc"],
        "work_project": ["source", "year_published", "types"],
        "match": {"types.source": "scienti", "types.level": 2, "source.publisher.name": {"$ne": float("nan")}},
    }
    sources = work_repository.get_works_with_sources_by_affiliation(affiliation_id, pipeline_params)
    return bar_parser.parse_annual_articles_by_top_publishers(sources)


def plot_most_used_title_words(affiliation_id: str, query_params: QueryParams) -> dict:
    data = calculations_repository.get_affiliation_calculations(affiliation_id)
    top_words = data.model_dump().get("top_words", None)
    if not top_words:
        return {
            "plot": [{"name": "Sin información", "value": 1, "percentage": 100}],
            "sum": 1,
        }
    return {"plot": top_words}


def plot_articles_by_publisher(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "source_project": ["publisher"],
        "work_project": ["source"],
        "match": {"types.source": "scienti", "types.level": 2, "types.code": {"$regex": "^11", "$options": ""}},
    }
    works = work_repository.get_works_with_sources_by_affiliation(affiliation_id, pipeline_params)
    return pie_parser.parse_articles_by_publisher(works)


def plot_products_by_subject(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"subjects": {"$ne": []}},
        "project": ["subjects"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return pie_parser.parse_products_by_subject(works)


def plot_products_by_database(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"updated": {"$ne": []}},
        "project": ["updated"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return pie_parser.parse_products_by_database(works)


def plot_articles_by_access_route(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {"types.source": "scienti", "types.level": 2, "types.code": {"$regex": "^11", "$options": ""}},
        "project": ["bibliographic_info"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    return pie_parser.parse_products_by_access_route(works)


def plot_products_by_author_sex(affiliation_id: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_products_by_author_sex(affiliation_id)
    return pie_parser.parse_products_by_author_sex(data)


def plot_products_by_author_age_range(affiliation_id: str, query_params: QueryParams) -> dict:
    works = plot_repository.get_products_by_author_age_and_affiliation(affiliation_id)
    return pie_parser.parse_products_by_age_range(works)


def plot_articles_by_scienti_category(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "project": ["ranking"],
    }
    works = work_repository.get_works_by_affiliation(affiliation_id, query_params, pipeline_params)
    total_works = work_repository.get_works_count_by_affiliation(affiliation_id)
    return pie_parser.parse_articles_by_scienti_category(works, total_works)


def plot_articles_by_scimago_quartile(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "source_project": ["ranking"],
        "work_project": ["source", "date_published"],
        "match": {"types.source": "scienti", "types.level": 2, "types.code": {"$regex": "^11", "$options": ""}},
    }
    works = work_repository.get_works_with_sources_by_affiliation(affiliation_id, pipeline_params)
    return pie_parser.parse_articles_by_scimago_quartile(works)


def plot_articles_by_publishing_institution(affiliation_id: str, query_params: QueryParams) -> dict:
    institution = database["affiliations"].find_one({"_id": ObjectId(affiliation_id)}, {"names": 1})
    pipeline_params = {
        "source_project": ["publisher"],
        "work_project": ["source"],
        "match": {"types.source": "scienti", "types.level": 2, "types.code": {"$regex": "^11", "$options": ""}},
    }
    works = work_repository.get_works_with_sources_by_affiliation(affiliation_id, pipeline_params)
    return pie_parser.parse_articles_by_publishing_institution(works, institution)


def plot_coauthorship_by_country_map(affiliation_id: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_coauthorship_by_country_map_by_affiliation(affiliation_id)
    return map_parser.parse_coauthorship_by_country_map(data)


def plot_coauthorship_by_colombian_department_map(affiliation_id: str, query_params: QueryParams) -> dict:
    data = plot_repository.get_coauthorship_by_colombian_department_map_by_affiliation(affiliation_id)
    return map_parser.get_coauthorship_by_colombian_department_map(data)


def plot_institutional_coauthorship_network(affiliation_id: str, query_params: QueryParams) -> dict:
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


def plot_annual_apc_expenses(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline_params = {
        "match": {
            "$and": [
                {"apc.charges": {"$exists": 1}},
                {"apc.currency": {"$exists": 1}},
            ]
        },
        "project": ["apc"],
    }
    sources = work_repository.get_works_with_sources_by_affiliation(affiliation_id, pipeline_params)
    return {"plot": bar_parser.apc_by_year(sources, 2022)}


def plot_apc_expenses_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str) -> dict:
    data = plot_repository.get_affiliations_apc_expenses_by_institution(affiliation_id, relation_type)
    return pie_parser.parse_apc_expenses_by_affiliations(data, 2022)

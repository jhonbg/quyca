from itertools import chain

from bson import ObjectId
from werkzeug.datastructures.structures import MultiDict

from database.repositories.person_repository import PersonRepository
from parsers import work_parser
from services import new_source_service
from services.actions.bar_action import BarAction
from services.actions.pie_action import PieAction
from services.actions.map_action import MapAction
from database.models.affiliation_model import Affiliation
from database.repositories.affiliation_repository import AffiliationRepository
from database.mongo import calculations_database, database
from database.repositories.plot_repository import PlotRepository
from database.repositories.work_repository import WorkRepository
from utils.mapping import get_openalex_scienti


class AffiliationService:
    @staticmethod
    def get_by_id(affiliation_id: str) -> Affiliation:
        return AffiliationRepository.get_affiliation_by_id(affiliation_id)

    @staticmethod
    def get_works_by_affiliation_csv(affiliation_id: str, affiliation_type: str) -> str:
        works = WorkRepository.get_works_by_affiliation(affiliation_id, affiliation_type)
        for work in works:
            if work.source.id:
                new_source_service.update_work_source(work)
                new_source_service.set_source_fields(work)
        return work_parser.parse_csv(works)

    @staticmethod
    def get_related_affiliations_by_affiliation(affiliation_id: str, affiliation_type: str) -> dict:
        data = {}
        if affiliation_type == "institution":
            faculties = AffiliationRepository.get_related_affiliations_by_type(
                affiliation_id, affiliation_type, "faculty"
            )

            data["faculties"] = [faculty.model_dump(include={"id", "name"}) for faculty in faculties]

        if affiliation_type in ["faculty", "institution"]:
            departments = AffiliationRepository.get_related_affiliations_by_type(
                affiliation_id, affiliation_type, "department"
            )

            data["departments"] = [department.modeld_dump(include={"id", "name"}) for department in departments]

        if affiliation_type in ["department", "faculty", "institution"]:
            groups = AffiliationRepository.get_related_affiliations_by_type(
                affiliation_id, affiliation_type, "group"
            )

            data["groups"] = [group.model_dump(include={"id", "name"}) for group in groups]


        if affiliation_type in ["group", "department", "faculty"]:
            authors = PersonRepository.get_persons_by_affiliation(affiliation_id)

            data["authors"] = [author.model_dump(include={"id", "full_name"}) for author in authors]


        return data


    @classmethod
    def get_affiliation_plot(cls, affiliation_id: str, affiliation_type: str, plot_type: str, query_params: MultiDict):
        if plot_type in ["type_faculty", "type_department", "type_group"]:
            affiliation_plot_type = plot_type.split("_")[-1]

            return cls.plot_affiliation_type(affiliation_id, affiliation_plot_type)

        if plot_type in ["citations_faculty", "citations_department", "citations_group"]:
            relation_type = plot_type.split("_")[-1]

            return cls.plot_citations_by_affiliations(affiliation_id, affiliation_type, relation_type)

        if plot_type in ["products_faculty", "products_department", "products_group"]:
            relation_type = plot_type.split("_")[-1]

            return cls.plot_products_by_affiliation(affiliation_id, affiliation_type, relation_type)
        
        if plot_type in ["apc_faculty", "apc_department", "apc_group"]:
            relation_type = plot_type.split("_")[-1]

            return cls.plot_apc_by_affiliation(affiliation_id, affiliation_type, relation_type)
        
        if plot_type in ["h_faculty", "h_department", "h_group"]:
            relation_type = plot_type.split("_")[-1]

            return cls.plot_h_by_affiliation(affiliation_id, affiliation_type, relation_type, query_params)

        return getattr(cls, "plot_" + plot_type)(affiliation_id, affiliation_type, query_params)


    @staticmethod
    def plot_year_type(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {"project": ["year_published", "types"]}

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
        )

        return {"plot": BarAction.get_by_work_year_and_work_type(works)}


    @staticmethod
    def plot_affiliation_type(affiliation_id: str, affiliation_plot_type: str, ):
        if affiliation_plot_type not in ["group", "department", "faculty"]:
            return None

        data = PlotRepository.get_bars_data_by_affiliation_type(affiliation_id, affiliation_plot_type)

        return {"plot": BarAction.get_by_affiliation_type(data)}


    @staticmethod
    def plot_year_citations(affiliation_id: str, affiliation_type: str, query_params):
        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params
        )

        return {"plot": BarAction.get_citations_by_year(works)}


    @staticmethod
    def plot_year_apc(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {
                "$and": [
                    {"apc.charges": {"$exists": 1}},
                    {"apc.currency": {"$exists": 1}},
                ]
            },
            "project": ["apc"],
        }

        sources = WorkRepository.get_sources_by_affiliation(
            affiliation_id,
            affiliation_type,
            pipeline_params
        )

        return {"plot": BarAction.apc_by_year(sources, 2022)}


    @staticmethod
    def plot_year_oa(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {
                "bibliographic_info.is_open_access": {"$ne": None},
                "year_published": {"$ne": None},
            },
            "project": ["year_published", "bibliographic_info"],
        }

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params,
        )

        return {"plot": BarAction.oa_by_year(works)}


    @staticmethod
    def plot_year_publisher(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            "project": ["publisher", "apc"],
        }

        sources = WorkRepository.get_sources_by_affiliation(
            affiliation_id,
            affiliation_type,
            pipeline_params
        )

        return {"plot": BarAction.works_by_publisher_year(sources)}


    @staticmethod
    def plot_year_h(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {"citations_by_year": {"$exists": 1}},
            "project": {"citations_by_year"}
        }

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
        )

        return {"plot": BarAction.h_index_by_year(works)}


    @staticmethod
    def plot_year_researcher(affiliation_id: str, affiliation_type: str, query_params):
        data = PlotRepository.get_bars_data_by_researcher_and_affiliation(affiliation_id, affiliation_type)
        plot = BarAction.works_by_researcher_category_and_year(data)

        if plot:
            return {"plot": plot}
        else:
            return {"plot": None}


    @staticmethod
    def plot_year_group(affiliation_id: str, affiliation_type: str, query_params):
        data = []
        groups = AffiliationRepository.get_groups_by_affiliation(affiliation_id, affiliation_type)

        for group in groups:
            pipeline_params = {
                "match": {"year_published": {"$ne": None}},
                "project": ["year_published", "date_published"],
            }

            works = WorkRepository.get_works_by_affiliation(
                str(group.id),
                "group",
                query_params,
                pipeline_params
            )

            for work in works:
                work.ranking = group.ranking

        return {"plot": BarAction.products_by_year_by_group_category(data)}


    @staticmethod
    def plot_title_words(affiliation_id: str, affiliation_type: str, query_params):
        data = calculations_database["affiliations"].find_one({"_id": ObjectId(affiliation_id)}, {"top_words": 1})

        if data:
            if not "top_words" in data.keys():
                return {"plot": None}
            data = data["top_words"]

            if not data:
                return {
                    "plot": [
                        {"name": "Sin información", "value": 1, "percentage": 100}
                    ],
                    "sum": 1,
                }

            return {"plot": data}
        else:
            return {"plot": None}


    @staticmethod
    def plot_citations_by_affiliations(affiliation_id: str, affiliation_type: str, relation_type: str):

        affiliations = AffiliationRepository.get_related_affiliations_by_type(
            affiliation_id, affiliation_type, relation_type
        )

        data = {}

        for affiliation in affiliations:
            data[affiliation.name] = WorkRepository.get_citations_count_by_affiliation(affiliation.id)

        return PieAction.get_citations_by_affiliation(data)


    @staticmethod
    def plot_products_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str):
        affiliations = AffiliationRepository.get_related_affiliations_by_type(
            affiliation_id, affiliation_type, relation_type
        )

        data = {}

        for affiliation in affiliations:
            data[affiliation.name] = WorkRepository.get_works_count_by_affiliation(affiliation.id, affiliation.types[0].type)

        total_works = WorkRepository.get_works_count_by_affiliation(affiliation_id, affiliation_type)

        return PieAction.get_products_by_affiliation(data, total_works)


    @staticmethod
    def plot_apc_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str):
        pipeline_params = {
            "match": {
                "$and": [
                    {"apc.charges": {"$exists": 1}},
                    {"apc.currency": {"$exists": 1}},
                ]
            },
            "project": ["apc", "affiliation_names"],
        }

        sources = WorkRepository.get_sources_by_related_affiliation(
            affiliation_id, affiliation_type, relation_type, pipeline_params
        )

        return PieAction.get_apc_by_sources(sources, 2022)


    @staticmethod
    def plot_h_by_affiliation(affiliation_id: str, affiliation_type: str, relation_type: str, query_params):
        affiliations = AffiliationRepository.get_related_affiliations_by_type(
            affiliation_id, affiliation_type, relation_type
        )

        data = {}

        pipeline_params = {
            "match": {"citations_count": {"$ne": []}},
            "project": ["citations_count"],
        }

        for affiliation in affiliations:
            works = WorkRepository.get_works_by_affiliation(
                affiliation.id,
                affiliation.types[0].type,
                query_params,
                pipeline_params
            )

            data[affiliation.name] = map(get_openalex_scienti, works)

        return PieAction.get_h_by_affiliation(data)


    @staticmethod
    def plot_products_publisher(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {"project": ["publisher"],}
        sources = WorkRepository.get_sources_by_affiliation(
            affiliation_id,
            affiliation_type,
            pipeline_params
        )

        data = map(
            lambda x: (
                x.publisher.name
                if x.publisher and isinstance(x.publisher.name, str)
                else "Sin información"
            ),
            sources,
        )

        return PieAction.get_products_by_publisher(data)


    @staticmethod
    def plot_products_subject(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {"subjects": {"$ne": []}},
            "project": ["subjects"],
        }

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
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

        return PieAction.get_products_by_subject(data)


    @staticmethod
    def plot_products_database(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {"updated": {"$ne": []}},
            "project": ["updated"],
        }

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
        )

        data = chain.from_iterable(map(lambda x: x.updated, works))

        return PieAction.get_products_by_database(data)


    @staticmethod
    def plot_products_oa(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {"project": ["bibliographic_info"],}
        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
        )

        data = map(
            lambda x: (
                x.bibliographic_info.open_access_status
                if x.bibliographic_info.open_access_status
                else "Sin información"
            ),
            works,
        )

        return PieAction.get_products_by_open_access(data)


    @staticmethod
    @PieAction.get_percentage
    def plot_products_sex(affiliation_id: str, affiliation_type: str, query_params):

        return PlotRepository.get_products_by_author_sex(affiliation_id)


    @staticmethod
    def plot_products_age(affiliation_id: str, affiliation_type: str, query_params):
        works = PlotRepository.get_products_by_author_age_and_affiliation(affiliation_id)

        result = PieAction.get_products_by_age(works)

        if result:
            return result
        else:
            return {"plot": None}


    @staticmethod
    def plot_scienti_rank(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {
            "match": {"ranking": {"$ne": []}},
            "project":["ranking"],
        }

        works = WorkRepository.get_works_by_affiliation(
            affiliation_id,
            affiliation_type,
            query_params,
            pipeline_params
            )

        total_works = WorkRepository.get_works_count_by_affiliation(affiliation_id, affiliation_type)
        data = chain.from_iterable(map(lambda x: x.ranking, works))

        return PieAction.get_products_by_scienti_rank(data, total_works)


    @staticmethod
    def plot_scimago_rank(affiliation_id: str, affiliation_type: str, query_params):
        pipeline_params = {"project": ["ranking"],}
        sources = WorkRepository.get_sources_by_affiliation(affiliation_id,affiliation_type,pipeline_params)
        data = chain.from_iterable(map(lambda x: x.ranking, sources))

        return PieAction.get_products_by_scimago_rank(data)


    @staticmethod
    def plot_published_institution(affiliation_id: str, affiliation_type: str, query_params):
        institution = database["affiliations"].find_one({"_id": ObjectId(affiliation_id)}, {"names": 1})
        pipeline_params = {"project": ["publisher"],}
        sources = WorkRepository.get_sources_by_affiliation(affiliation_id, affiliation_type, pipeline_params)

        return PieAction.get_products_by_same_institution(sources, institution)


    @staticmethod
    def plot_collaboration_worldmap(affiliation_id: str, affiliation_type: str, query_params):
        data = PlotRepository.get_collaboration_worldmap_by_affiliation(affiliation_id, affiliation_type)

        result = MapAction.get_collaboration_worldmap(data)

        if result:
            return {"plot": result}
        else:
            return {"plot": None}


    @staticmethod
    def plot_collaboration_colombiamap(affiliation_id: str, affiliation_type: str, query_params):
        data = PlotRepository.get_collaboration_colombiamap_by_affiliation(affiliation_id, affiliation_type)

        return {"plot": MapAction.get_collaboration_colombiamap(data)}


    @staticmethod
    def plot_collaboration_network(affiliation_id: str, affiliation_type: str, query_params):
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

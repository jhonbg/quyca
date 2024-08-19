from itertools import chain

from bson import ObjectId

from actions.bar_action import BarAction
from actions.map_action import MapAction
from actions.pie_action import PieAction
from models.person_model import Person
from repositories.mongo import calculations_database, database
from repositories.person_repository import PersonRepository
from repositories.plot_repository import PlotRepository
from repositories.work_repository import WorkRepository


class PersonService:
    @staticmethod
    def get_by_id(person_id: str) -> Person:
        return PersonRepository.get_by_id(person_id)


    @classmethod
    def get_person_plot(cls, person_id: str, query_params):
        return getattr(cls, "plot_" + query_params.get("plot"))(person_id, query_params)


    @staticmethod
    def plot_year_type(person_id: str, query_params):

        works = WorkRepository.get_works_by_person(person_id, query_params)

        return {"plot": BarAction.get_by_work_year_and_work_type(works)}


    @staticmethod
    def plot_year_citations(person_id: str, query_params):
        works = WorkRepository.get_works_by_person(person_id, query_params)

        return {"plot": BarAction.get_citations_by_year(works)}


    @staticmethod
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

        sources = WorkRepository.get_sources_by_person(person_id, query_params, pipeline_params)

        return {"plot": BarAction.apc_by_year(sources, 2022)}


    @staticmethod
    def plot_year_oa(person_id: str, query_params):
        pipeline_params = {
            "match": {
                "bibliographic_info.is_open_access": {"$ne": None},
                "year_published": {"$ne": None},
            },
            "project": ["year_published", "bibliographic_info"],
        }

        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

        return {"plot": BarAction.oa_by_year(works)}


    @staticmethod
    def plot_year_publisher(person_id: str, query_params):
        pipeline_params = {
            "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            "project": ["publisher", "apc"],
        }

        sources = WorkRepository.get_sources_by_person(person_id, query_params, pipeline_params)

        return {"plot": BarAction.works_by_publisher_year(sources)}


    @staticmethod
    def plot_year_h(person_id: str, query_params):
        pipeline_params = {
            "match": {"citations_by_year": {"$exists": 1}},
            "project": {"citations_by_year"}
        }

        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

        return {"plot": BarAction.h_index_by_year(works)}


    @staticmethod
    def plot_year_researcher(person_id: str, query_params):
        data = PlotRepository.get_bars_data_by_researcher_and_person(person_id)
        plot = BarAction.works_by_researcher_category_and_year(data)

        if plot:
            return {"plot": plot}
        else:
            return {"plot": None}


    @staticmethod
    def plot_title_words(person_id: str, query_params):
        data = calculations_database["person"].find_one({"_id": ObjectId(person_id)}, {"top_words": 1})

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
    def plot_products_publisher(person_id: str, query_params):
        pipeline_params = {
            "match": {"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            "project": ["publisher"]
        }

        sources = WorkRepository.get_sources_by_person(person_id, query_params, pipeline_params)

        data = map(lambda x: x.publisher.name, sources)

        return PieAction.get_products_by_publisher(data)


    @staticmethod
    def plot_products_subject(person_id: str, query_params):
        pipeline_params = {
            "match": {"subjects": {"$ne": []}},
            "project": ["subjects"],
        }

        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

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
    def plot_products_database(person_id: str, query_params):
        pipeline_params = {
            "match": {"updated": {"$ne": []}},
            "project": ["updated"],
        }

        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

        data = chain.from_iterable(map(lambda x: x.updated, works))

        return PieAction.get_products_by_database(data)


    @staticmethod
    def plot_products_oa(person_id: str, query_params):
        pipeline_params = {
            "match": {"bibliographic_info.open_access_status": {"$exists": 1}},
            "project": ["bibliographic_info"]
        }
        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

        data = map(lambda x: x.bibliographic_info.open_access_status, works)

        return PieAction.get_products_by_open_access(data)


    @staticmethod
    def plot_products_age(person_id: str, query_params):
        works = PlotRepository.get_products_by_author_age_and_person(person_id)

        result = PieAction.get_products_by_age(works)

        if result:
            return result
        else:
            return {"plot": None}


    @staticmethod
    def plot_scienti_rank(person_id: str, query_params):
        pipeline_params = {
            "match": {"ranking": {"$ne": []}},
            "project": ["ranking"],
        }

        works = WorkRepository.get_works_by_person(person_id, query_params, pipeline_params)

        data = chain.from_iterable(map(lambda x: x.ranking, works))

        return PieAction.get_products_by_scienti_rank(data)


    @staticmethod
    def plot_scimago_rank(person_id: str, query_params):
        pipeline_params = {"project": ["ranking"], }
        sources = WorkRepository.get_sources_by_person(person_id, query_params, pipeline_params)
        data = chain.from_iterable(map(lambda x: x.ranking, sources))

        return PieAction.get_products_by_scimago_rank(data)


    @staticmethod
    def plot_published_institution(person_id: str, query_params):
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
        pipeline_params = {"project": ["publisher"], }
        sources = WorkRepository.get_sources_by_person(person_id, query_params, pipeline_params)

        return PieAction.get_products_by_same_institution(sources, institution)


    @staticmethod
    def plot_collaboration_worldmap(person_id: str, query_params):
        data = PlotRepository.get_collaboration_worldmap_by_person(person_id)

        result = MapAction.get_collaboration_worldmap(data)

        if result:
            return {"plot": result}
        else:
            return {"plot": None}


    @staticmethod
    def plot_collaboration_colombiamap(person_id: str, query_params):
        data = PlotRepository.get_collaboration_colombiamap_by_person(person_id)

        return {"plot": MapAction.get_collaboration_colombiamap(data)}


    @staticmethod
    def plot_collaboration_network(person_id: str, query_params):
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
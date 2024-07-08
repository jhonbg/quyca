from math import nan
from typing import Any, Callable
from itertools import chain

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from infraestructure.mongo.utils.session import client
from infraestructure.mongo.repositories.work import WorkRepository
from infraestructure.mongo.repositories.affiliation import affiliation_repository
from infraestructure.mongo.models.source import Source
from core.config import settings
from utils.bars import bars
from utils.maps import maps
from utils.pies import pies


class PersonAppService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]
        self.bars = bars()
        self.pies = pies()
        self.maps = maps()

    def get_info(self, idx, start_year=None, end_year=None):
        initial_year = 9999
        final_year = 0

        if start_year:
            try:
                start_year = int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year = int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        person = self.colav_db["person"].find_one({"_id": ObjectId(idx)})
        if person:
            aff_id = None
            affiliation = None
            for aff in person["affiliations"]:
                if aff_id:
                    break
                for typ in aff["types"]:
                    if not typ["type"] in ["group", "faculty", "department"]:
                        aff_id = aff["id"]
                        break
            if aff_id:
                affiliation = self.colav_db["affiliations"].find_one(
                    {"_id": ObjectId(aff_id)}
                )
            logo = ""
            if affiliation:
                if "external_urls" in affiliation.keys():
                    for ext in affiliation["external_urls"]:
                        if ext["source"] == "logo":
                            logo = ext["url"]

            entry = {
                "id": person["_id"],
                "name": person["full_name"],
                "citations_count": WorkRepository.count_citations_by_author(
                    author_id=idx
                ),
                "products_count": WorkRepository.count_papers_by_author(author_id=idx),
                "external_urls": (
                    [
                        ext
                        for ext in person["external_urls"]
                        if ext["source"] not in ["logo"]
                    ]
                    if "external_urls" in person.keys()
                    else None
                ),
                "external_ids": (
                    [
                        ext
                        for ext in person["external_ids"]
                        if ext["source"]
                        not in [
                            "Cédula de Ciudadanía",
                            "Cédula de Extranjería",
                            "Passport",
                        ]
                    ]
                    if "external_ids" in person.keys()
                    else None
                ),
                "logo": logo,
                "affiliations": person["affiliations"],
            }
            index_list = []

            filters = {"years": {}}
            for reg in (
                self.colav_db["works"]
                .find({"authors.id": ObjectId(idx), "year_published": {"$exists": 1}})
                .sort([("year_published", ASCENDING)])
                .limit(1)
            ):
                filters["years"]["start_year"] = reg["year_published"]
            for reg in (
                self.colav_db["works"]
                .find({"authors.id": ObjectId(idx), "year_published": {"$exists": 1}})
                .sort([("year_published", DESCENDING)])
                .limit(1)
            ):
                filters["years"]["end_year"] = reg["year_published"]
            filters["types"] = []

            return {"data": entry, "filters": filters}
        else:
            return None

    def get_products_by_year_by_type(self, idx: str):
        data = []
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx, project=["year_published", "types"], available_filters=False
        )
        result = self.bars.products_by_year_by_type(works)
        return {"plot": result}

    def get_citations_by_year(self, idx: str):
        _match = {"citations_by_year": {"$ne": []}, "year_published": {"$exists": 1}}
        data, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            project=["year_published", "citations_by_year"],
            match=_match,
            available_filters=False,
        )
        result = self.bars.citations_by_year(data)
        return {"plot": result}

    def get_apc_by_year(self, idx: str):
        sources = WorkRepository.get_sources_by_author(
            idx,
            match={
                "$and": [
                    {"apc.charges": {"$exists": 1}},
                    {"apc.currency": {"$exists": 1}},
                ]
            },
            project=["apc"],
        )
        _data = map(lambda x: x.apc, sources)
        return {"plot": self.bars.apc_by_year(_data, 2022)}

    def get_oa_by_year(self, idx: str):
        _match = {
            "bibliographic_info.is_open_access": {"$ne": None},
            "year_published": {"$ne": None},
        }
        data, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match=_match,
            available_filters=False,
            project=["year_published", "bibliographic_info"],
        )
        result = self.bars.oa_by_year(data)
        return {"plot": result}

    def get_products_by_year_by_publisher(self, idx: str):
        sources = WorkRepository.get_sources_by_author(
            idx,
            match={"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            project=["publisher", "apc"],
        )
        result = self.bars.products_by_year_by_publisher(sources)
        return {"plot": result}

    def get_h_by_year(self, idx: str):
        _match = {"citations_by_year": {"$exists": 1}}
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match=_match,
            project=["citations_by_year"],
            available_filters=False,
        )
        result = self.bars.h_index_by_year(works)
        return {"plot": result}

    def get_products_by_year_by_researcher_category(self, idx: str):
        data = []
        pipeline = [
            {"$match": {"authors.id": ObjectId(idx)}},
            {"$project": {"year_published": 1, "authors": 1}},
            {"$unwind": "$authors"},
            {"$match": {"authors.id": ObjectId(idx)}},
            {
                "$lookup": {
                    "from": "person",
                    "localField": "authors.id",
                    "foreignField": "_id",
                    "as": "researcher",
                }
            },
            {"$project": {"year_published": 1, "researcher.ranking": 1}},
            {"$match": {"researcher.ranking.source": "scienti"}},
        ]
        for work in self.colav_db["works"].aggregate(pipeline):
            for researcher in work["researcher"]:
                for rank in researcher["ranking"]:
                    if rank["source"] == "scienti":
                        data.append(
                            {
                                "year_published": work["year_published"],
                                "rank": rank["rank"],
                            }
                        )
        if not data:
            return {"plot": None}
        result = self.bars.products_by_year_by_researcher_category(data)
        if result:
            return {"plot": result}
        else:
            return {"plot": None}

    def get_title_words(self, idx: int):
        data = self.impactu_db["person"].find_one(
            {"_id": ObjectId(idx)}, {"top_words": 1}
        )
        if data:
            if not "top_words" in data.keys():
                return {"plot": None}
            data = data["top_words"]
            return {"plot": data} if len(data) > 5 else self.pies.title_words(data)
        else:
            return {"plot": None}

    def get_products_by_publisher(self, idx: int):
        sources = WorkRepository.get_sources_by_author(
            idx,
            match={"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            project=["publisher"],
        )
        data = map(lambda x: x.publisher.name, sources)
        return self.pies.products_by_publisher(data)

    def get_products_by_subject(self, idx: str, level: int = 0):
        data = []
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match={"subjects": {"$ne": []}},
            available_filters=False,
            project=["subjects"],
        )
        data = chain.from_iterable(
            map(
                lambda x: [
                    sub
                    for subject in x.subjects
                    for sub in subject.subjects
                    if subject.source == "openalex" and sub.level == level
                ],
                works,
            )
        )
        result = self.pies.products_by_subject(data)
        return result

    def get_products_by_database(self, idx: str):
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match={"updated": {"$ne": []}},
            available_filters=False,
            project=["updated"],
        )
        data = chain.from_iterable(map(lambda x: x.updated, works))
        result = self.pies.products_by_database(data)
        return result

    def get_products_by_open_access_status(self, idx):
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match={"bibliographic_info.open_access_status": {"$exists": 1}},
            available_filters=False,
            project=["bibliographic_info"],
        )
        _data = map(lambda x: x.bibliographic_info.open_access_status, works)
        result = self.pies.products_by_open_access_status(_data)
        return result

    def get_products_by_author_age(self, idx):
        data = []
        pipeline = [
            {"$match": {"authors.id": ObjectId(idx)}},
            {"$project": {"authors": 1, "date_published": 1, "year_published": 1}},
            {"$unwind": "$authors"},
            {"$match": {"authors.id": ObjectId(idx)}},
            {
                "$lookup": {
                    "from": "person",
                    "localField": "authors.id",
                    "foreignField": "_id",
                    "as": "author",
                }
            },
            {
                "$project": {
                    "author.birthdate": 1,
                    "date_published": 1,
                    "year_published": 1,
                }
            },
            {"$match": {"author.birthdate": {"$ne": -1, "$exists": 1}}},
        ]
        for work in self.colav_db["works"].aggregate(pipeline):
            data.append(work)
        print(data)
        result = self.pies.products_by_age(data)
        return result

    def get_products_by_scienti_rank(self, idx):
        works, _ = WorkRepository.get_research_products_by_author_iterator(
            author_id=idx,
            match={"ranking": {"$ne": []}},
            available_filters=False,
            project=["ranking"],
        )
        _data = chain.from_iterable(map(lambda x: x.ranking, works))
        return self.pies.products_by_scienti_rank(_data)

    def get_products_by_scimago_rank(self, idx):
        sources = WorkRepository.get_sources_by_author(idx, project=["source", "date_published"])
        _data = chain.from_iterable(map(lambda x: x.ranking, sources))
        total_works = WorkRepository.count_papers_by_author(author_id=idx)
        return self.pies.products_by_scimago_rank(_data, total_works)

    def get_publisher_same_institution(self, idx):
        data = []
        inst_id = None
        person = self.colav_db["person"].find_one(
            {"_id": ObjectId(idx)}, {"affiliations": 1}
        )
        found = False
        for aff in person["affiliations"]:
            if found:
                break
            for typ in aff["types"]:
                if not typ["type"] in ["faculty", "department", "group"]:
                    inst_id = aff["id"]
                    found = True
                    break
        institution = self.colav_db["affiliations"].find_one(
            {"_id": ObjectId(inst_id)}, {"names": 1}
        )
        pipeline = [
            {"$match": {"authors.id": ObjectId(idx)}},
            {"$project": {"source": 1}},
            {
                "$lookup": {
                    "from": "sources",
                    "localField": "source.id",
                    "foreignField": "_id",
                    "as": "source",
                }
            },
            {"$unwind": "$source"},
            {"$project": {"source.publisher": 1}},
            {
                "$match": {
                    "source.publisher": {"$ne": nan, "$exists": 1, "$ne": ""},
                    "source.publisher.name": {"$ne": nan},
                }
            },
        ]
        data = map(lambda x: Source(**x["source"]), self.colav_db["works"].aggregate(pipeline))
        return self.pies.products_editorial_same_institution(data, institution)

    def get_coauthorships_worldmap(self, idx):
        data = []
        pipeline = [
            {"$match": {"authors.id": ObjectId(idx)}},
            {"$unwind": "$authors"},
            {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
            {"$unwind": "$_id"},
            {
                "$lookup": {
                    "from": "affiliations",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "affiliation",
                }
            },
            {
                "$project": {
                    "count": 1,
                    "affiliation.addresses.country_code": 1,
                    "affiliation.addresses.country": 1,
                }
            },
            {"$unwind": "$affiliation"},
            {"$unwind": "$affiliation.addresses"},
        ]
        for work in self.colav_db["works"].aggregate(pipeline):
            data.append(work)
        result = self.maps.get_coauthorship_world_map(data)
        return {"plot": result}

    def get_coauthorships_colombiamap(self, idx):
        data = []
        pipeline = [
            {"$match": {"authors.id": ObjectId(idx)}},
            {"$unwind": "$authors"},
            {"$group": {"_id": "$authors.affiliations.id", "count": {"$sum": 1}}},
            {"$unwind": "$_id"},
            {
                "$lookup": {
                    "from": "affiliations",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "affiliation",
                }
            },
            {
                "$project": {
                    "count": 1,
                    "affiliation.addresses.country_code": 1,
                    "affiliation.addresses.city": 1,
                }
            },
            {"$unwind": "$affiliation"},
            {"$unwind": "$affiliation.addresses"},
        ]
        for work in self.colav_db["works"].aggregate(pipeline):
            data.append(work)
        result = self.maps.get_coauthorship_colombia_map(data)
        return {"plot": result}

    def get_coauthorships_network(self, idx):
        data = self.impactu_db["person"].find_one(
            {"_id": ObjectId(idx)}, {"coauthorship_network": 1}
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

    @property
    def plot_mapping(self) -> dict[str, Callable[[Any, Any], dict[str, list] | None]]:
        return {
            "year_type": self.get_products_by_year_by_type,
            "year_citations": self.get_citations_by_year,
            "year_apc": self.get_apc_by_year,
            "year_oa": self.get_oa_by_year,
            "year_publisher": self.get_products_by_year_by_publisher,
            "year_h": self.get_h_by_year,
            "year_researcher": self.get_products_by_year_by_researcher_category,
            # "year_group": self.get_products_by_year_by_group_category,
            "title_words": self.get_title_words,
            # "citations_affiliations": self.get_citations_by_affiliations,
            # "products_affiliations": self.get_products_by_affiliations,
            # "apc_affiliations": self.get_apc_by_affiliations,
            # "h_affiliations": self.get_h_by_affiliations,
            "products_publisher": self.get_products_by_publisher,
            "products_subject": self.get_products_by_subject,
            "products_database": self.get_products_by_database,
            "products_oa": self.get_products_by_open_access_status,
            # "products_sex": self.get_products_by_author_sex,
            "products_age": self.get_products_by_author_age,
            "scienti_rank": self.get_products_by_scienti_rank,
            "scimago_rank": self.get_products_by_scimago_rank,
            "published_institution": self.get_publisher_same_institution,
            "collaboration_worldmap": self.get_coauthorships_worldmap,
            "collaboration_colombiamap": self.get_coauthorships_colombiamap,
            "collaboration_network": self.get_coauthorships_network,
        }


person_app_service = PersonAppService()

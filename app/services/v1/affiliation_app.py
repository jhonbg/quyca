from typing import Any, Callable
from itertools import chain

from bson import ObjectId

from infraestructure.mongo.utils.session import client
from infraestructure.mongo.repositories.work import WorkRepository
from infraestructure.mongo.repositories.affiliation import (
    AffiliationRepository,
    affiliation_repository,
)
from infraestructure.mongo.repositories.affiliation_calculations import (
    affiliation_calculations_repository,
)
from infraestructure.mongo.models.work import Work
from core.config import settings
from utils.bars import bars
from utils.maps import maps
from utils.pies import pies
from schemas.affiliation import AffiliationRelatedInfo


def get_openalex_scienti(x: Work):
    for count in x.citations_count:
        if count.source == "openalex":
            return count.count
        if count.source == "scienti":
            return count.count
    return 0


def get_subjects(work: Work, level: int = 0):
    for subject in work.subjects:
        for sub in subject.subjects:
            if subject.source == "openalex" and sub.level == level:
                return sub


class AffiliationAppService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]
        self.bars = bars()
        self.pies = pies()
        self.maps = maps()

    def get_info(self, idx, typ, start_year=None, end_year=None):

        pipeline = [
            {"$match": {"_id": ObjectId(idx)}},
            {
                "$project": {
                    "_id": 1,
                    "names": 1,
                    "citations": 1,
                    "external_urls": 1,
                    "types": 1,
                    "external_ids": 1,
                    "addresses": 1,
                    "relations": 1,
                }
            },
        ]

        affiliation = next(self.colav_db["affiliations"].aggregate(pipeline), None)
        if affiliation:
            name = ""
            for n in affiliation["names"]:
                if n["lang"] == "es":
                    name = n["name"]
                    break
                elif n["lang"] == "en":
                    name = n["name"]
            logo = ""
            for ext in affiliation["external_urls"]:
                if ext["source"] == "logo":
                    logo = ext["url"]

            entry = {
                "id": affiliation["_id"],
                "name": name,
                "citations_count": affiliation_calculations_repository.get_by_id(
                    id=idx
                ).citations_count,
                "products_count": WorkRepository.count_papers(
                    affiliation_id=affiliation["_id"],
                    affiliation_type=affiliation["types"][0]["type"],
                ),
                "external_urls": [
                    ext
                    for ext in affiliation["external_urls"]
                    if ext["source"] != "logo"
                ],
                "external_ids": affiliation["external_ids"],
                "types": affiliation["types"],
                "addresses": affiliation["addresses"],
                "logo": logo,
            }
            affiliations, upside_logo = AffiliationRepository.upside_relations(
                affiliation["relations"], typ
            )

            entry.update(
                {
                    "affiliations": affiliations,
                    "logo": upside_logo if upside_logo else logo,
                }
            )

            return {"data": entry}
        else:
            return None

    def get_affiliations(
        self, idx, typ=None, aff_type: str | None = None
    ) -> dict[str, list[Any]]:
        data = {}
        if typ == "institution":
            data["faculties"] = affiliation_repository.get_affiliations_related_type(
                idx, "faculty", typ
            )
        if typ in ["faculty", "institution"]:
            data["departments"] = affiliation_repository.get_affiliations_related_type(
                idx, "department", typ
            )
        if typ in ["department", "faculty", "institution"]:
            data["groups"] = affiliation_repository.get_affiliations_related_type(
                idx, "group", typ
            )
        if typ in ["group", "department", "faculty"]:
            data["authors"] = affiliation_repository.get_authors_by_affiliation(
                idx, typ
            )

        result = AffiliationRelatedInfo.model_validate(data, from_attributes=True)

        return result.model_dump(exclude_none=True)

    def get_products_by_year_by_type(self, idx, typ=None, aff_type: str | None = None):
        data, f = WorkRepository.get_research_products_by_affiliation_iterator(
            idx, aff_type, project=["year_published", "types"], available_filters=False
        )
        return {"plot": self.bars.products_by_year_by_type(data)}

    def get_products_by_affiliation_by_type(
        self, idx, typ, aff_type: str | None = None
    ):
        if not typ in ["group", "department", "faculty"]:
            return None
        pipeline = [
            {
                "$match": {
                    "affiliations.types.type": typ,
                    "affiliations.id": ObjectId(idx),
                }
            },
            {"$unwind": "$affiliations"},
            {"$match": {"affiliations.types.type": typ}},
            {"$project": {"authorIds": "$_id", "_id": 0, "affiliations": 1}},
            {
                "$lookup": {
                    "from": "works",
                    "localField": "authorIds",
                    "foreignField": "authors.id",
                    "as": "works",
                }
            },
            {"$unwind": "$works"},
            {"$match": {"works.types": {"$ne": []}}},
            {
                "$project": {
                    "name": "$affiliations.name",
                    "work": {"types": "$works.types"},
                }
            },
        ]
        data = {}
        for _data in self.colav_db["person"].aggregate(pipeline):
            if not data.get(_data["name"], False):
                data[_data["name"]] = []
            data[_data["name"]].append(_data["work"])

        return {"plot": self.bars.products_by_affiliation_by_type(data)}

    def get_citations_by_year(self, idx, typ=None, aff_type: str | None = None):
        data, f = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            available_filters=False,
            project=["citations_by_year", "year_published"],
        )
        return {"plot": self.bars.citations_by_year(data)}

    def get_apc_by_year(self, idx, typ=None, aff_type: str | None = None):
        sources = WorkRepository.get_sources_by_affiliation(
            idx,
            aff_type,
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

    def get_oa_by_year(self, idx, typ=None, aff_type: str | None = None):

        _match = {
            "bibliographic_info.is_open_access": {"$ne": None},
            "year_published": {"$ne": None},
        }
        data, f = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            match=_match,
            available_filters=False,
            project=["year_published", "bibliographic_info"],
        )
        return {"plot": self.bars.oa_by_year(data)}

    def get_products_by_year_by_publisher(
        self, idx, typ=None, aff_type: str | None = None
    ):
        sources = WorkRepository.get_sources_by_affiliation(
            idx,
            aff_type,
            match={"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            project=["publisher", "apc"],
        )
        return {"plot": self.bars.products_by_year_by_publisher(sources)}

    def get_h_by_year(self, idx, typ=None, aff_type: str | None = None):
        _match = {"citations_by_year": {"$exists": 1}}
        works, f = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            match=_match,
            available_filters=False,
            project={"citations_by_year"},
        )
        return {"plot": self.bars.h_index_by_year(works)}

    def get_products_by_year_by_researcher_category(
        self, idx, typ=None, aff_type: str | None = None
    ):
        data = []
        if typ in ["group", "department", "faculty"]:
            for author in self.colav_db["person"].find(
                {"affiliations.id": ObjectId(idx)}, {"affiliations": 1}
            ):
                pipeline = [
                    {
                        "$match": {
                            "authors.id": author["_id"],
                            "year_published": {"$ne": None},
                        }
                    },
                    {"$project": {"year_published": 1, "authors": 1}},
                    {"$unwind": "$authors"},
                    {
                        "$lookup": {
                            "from": "person",
                            "localField": "authors.id",
                            "foreignField": "_id",
                            "as": "researcher",
                        }
                    },
                    {
                        "$project": {
                            "year_published": 1,
                            "researcher.ranking": 1,
                            "researcher._id": 1,
                        }
                    },
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
        else:
            pipeline = [
                {
                    "$match": {
                        "authors.affiliations.id": ObjectId(idx),
                        "year_published": {"$ne": None},
                    }
                },
                {"$project": {"year_published": 1, "authors": 1}},
                {"$unwind": "$authors"},
                {"$match": {"authors.affiliations.id": ObjectId(idx)}},
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
        result = self.bars.products_by_year_by_researcher_category(data)
        if result:
            return {"plot": result}
        else:
            return {"plot": None}

    def get_products_by_year_by_group_category(
        self, idx, typ=None, aff_type: str | None = None
    ):
        data = []
        groups = affiliation_repository.get_groups_by_affiliation(idx, aff_type)
        for group in groups:
            works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
                str(group.id),
                "group",
                match={"year_published": {"$ne": None}},
                available_filters=False,
                project=["year_published", "date_published"],
            )
            for work in works:
                work.ranking_ = group.ranking
                data.append(work)
        result = self.bars.products_by_year_by_group_category(data)
        return {"plot": result}

    def get_title_words(self, idx, typ=None, aff_type: str | None = None):
        data = self.impactu_db["affiliations"].find_one(
            {"_id": ObjectId(idx)}, {"top_words": 1}
        )
        if data:
            if not "top_words" in data.keys():
                return {"plot": None}
            data = data["top_words"]
            return {"plot": data}
        else:
            return {"plot": None}

    def get_citations_by_affiliations(self, idx, typ, aff_type: str | None = None):
        if not typ in ["group", "department", "faculty"]:
            return None
        affiliations = affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        _data = {}
        for aff in affiliations:
            _data[aff.name], _ = (
                WorkRepository.get_research_products_by_affiliation_iterator(
                    aff.id,
                    aff.types[0].type,
                    match={"citations_count": {"$ne": []}},
                    available_filters=False,
                )
            )
        return self.pies.citations_by_affiliation(_data)

    def get_products_by_affiliations(self, idx, typ, aff_type: str | None = None):
        affiliations = affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        data = {}
        for aff in affiliations:
            data[aff.name] = WorkRepository.count_papers(
                affiliation_id=aff.id, affiliation_type=aff.types[0].type
            )
        total_works = WorkRepository.count_papers(
            affiliation_id=idx, affiliation_type=aff_type
        )
        return self.pies.products_by_affiliation(data, total_works)

    def get_apc_by_affiliations(self, idx, typ, aff_type: str | None = None):
        affiliations = affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        data = {}
        for aff in affiliations:
            sources = WorkRepository.get_sources_by_affiliation(
                aff.id,
                aff.types[0].type,
                match={
                    "$and": [
                        {"apc.charges": {"$exists": 1}},
                        {"apc.currency": {"$exists": 1}},
                    ]
                },
                project=["apc"],
            )
            data[aff.name] = map(lambda x: x.apc, sources)
        return self.pies.apc_by_affiliation(data, 2022)

    def get_h_by_affiliations(self, idx, typ, aff_type: str | None = None):
        affiliations = affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        _data = {}
        for aff in affiliations:
            works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
                aff.id,
                aff.types[0].type,
                match={"citations_count": {"$ne": []}},
                available_filters=False,
                project=["citations_count"],
            )
            _data[aff.name] = map(
                get_openalex_scienti,
                works,
            )
        return self.pies.hindex_by_affiliation(_data)

    def get_products_by_publisher(self, idx, typ=None, aff_type: str | None = None):
        sources = WorkRepository.get_sources_by_affiliation(
            idx,
            aff_type,
            project=["publisher"],
        )
        data = map(
            lambda x: x.publisher.name if x.publisher else "Sin información", sources
        )
        return self.pies.products_by_publisher(data)

    def get_products_by_subject(
        self, idx, level: int = 0, typ: str = None, aff_type: str | None = None
    ):
        works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
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
        return self.pies.products_by_subject(data)

    def get_products_by_database(self, idx, typ=None, aff_type: str | None = None):
        works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            match={"updated": {"$ne": []}},
            available_filters=False,
            project=["updated"],
        )
        data = chain.from_iterable(map(lambda x: x.updated, works))
        return self.pies.products_by_database(data)

    def get_products_by_open_access_status(
        self, idx, typ=None, aff_type: str | None = None
    ):
        works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            available_filters=False,
            project=["bibliographic_info"],
        )
        _data = map(
            lambda x: (
                x.bibliographic_info.open_access_status
                if x.bibliographic_info.open_access_status
                else "Sin información"
            ),
            works,
        )
        result = self.pies.products_by_open_access_status(_data)
        return result

    def get_products_by_author_sex(self, idx, typ=None, aff_type: str | None = None):
        data = []
        if typ in ["group", "department", "faculty"]:
            for author in self.colav_db["person"].find(
                {"affiliations.id": ObjectId(idx)}, {"affiliations": 1}
            ):
                pipeline = [
                    {"$match": {"authors.id": author["_id"]}},
                    {"$project": {"authors": 1}},
                    {"$unwind": "$authors"},
                    {
                        "$lookup": {
                            "from": "person",
                            "localField": "authors.id",
                            "foreignField": "_id",
                            "as": "author",
                        }
                    },
                    {"$project": {"author.sex": 1}},
                    # {"$match": {"author.sex": {"$ne": "", "$exists": 1}}},
                ]
                for work in self.colav_db["works"].aggregate(pipeline):
                    data.append(work)
        else:
            pipeline = [
                {"$match": {"authors.affiliations.id": ObjectId(idx)}},
                {"$project": {"authors": 1}},
                {"$unwind": "$authors"},
                {
                    "$lookup": {
                        "from": "person",
                        "localField": "authors.id",
                        "foreignField": "_id",
                        "as": "author",
                    }
                },
                {"$project": {"author.sex": 1}},
                # {"$match": {"author.sex": {"$ne": "", "$exists": 1}}},
            ]
            for work in self.colav_db["works"].aggregate(pipeline):
                data.append(work)

        result = self.pies.products_by_sex(data)
        if result:
            return result
        else:
            return {"plot": None}

    def get_products_by_author_age(self, idx, typ=None, aff_type: str | None = None):
        data = []
        if typ in ["group", "department", "faculty"]:
            for author in self.colav_db["person"].find(
                {"affiliations.id": ObjectId(idx)}, {"affiliations": 1}
            ):
                pipeline = [
                    {
                        "$match": {
                            "authors.id": author["_id"],
                            # "date_published": {"$ne": None},
                        },
                    },
                    {"$unwind": "$authors"},
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
                    # {"$match": {"author.birthdate": {"$nin": [-1, ""], "$exists": 1}}},
                ]
                for work in self.colav_db["works"].aggregate(pipeline):
                    data.append(work)
        else:
            pipeline = [
                {
                    "$match": {
                        "authors.affiliations.id": ObjectId(idx),
                        # "date_published": {"$ne": None},
                    }
                },
                {"$unwind": "$authors"},
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
                # {"$match": {"author.birthdate": {"$nin": [-1, ""], "$exists": 1}}},
            ]
            for work in self.colav_db["works"].aggregate(pipeline):
                data.append(work)

        result = self.pies.products_by_age(data)
        if result:
            return result
        else:
            return {"plot": None}

    def get_products_by_scienti_rank(self, idx, typ=None, aff_type: str | None = None):
        works, _ = WorkRepository.get_research_products_by_affiliation_iterator(
            idx,
            aff_type,
            match={"ranking": {"$ne": []}},
            available_filters=False,
            project=["ranking"],
        )
        total_works = WorkRepository.count_papers(
            affiliation_id=idx, affiliation_type=aff_type
        )
        _data = chain.from_iterable(map(lambda x: x.ranking, works))
        return self.pies.products_by_scienti_rank(_data, total_works)

    def get_products_by_scimago_rank(self, idx, typ=None, aff_type: str | None = None):
        sources = WorkRepository.get_sources_by_affiliation(
            idx,
            aff_type,
            project=["ranking"],
        )
        _data = chain.from_iterable(map(lambda x: x.ranking, sources))
        return self.pies.products_by_scimago_rank(_data)

    def get_publisher_same_institution(
        self, idx, typ=None, aff_type: str | None = None
    ):
        institution = self.colav_db["affiliations"].find_one(
            {"_id": ObjectId(idx)}, {"names": 1}
        )
        sources = WorkRepository.get_sources_by_affiliation(
            idx, aff_type, project=["publisher"]
        )
        return self.pies.products_editorial_same_institution(sources, institution)

    def get_coauthorships_worldmap(self, idx, typ=None, aff_type: str | None = None):
        data = []
        if typ in ["group", "department", "faculty"]:
            for author in self.colav_db["person"].find(
                {"affiliations.id": ObjectId(idx)}, {"affiliations": 1}
            ):
                pipeline = [
                    {"$match": {"authors.id": author["_id"]}},
                    {"$unwind": "$authors"},
                    {
                        "$group": {
                            "_id": "$authors.affiliations.id",
                            "count": {"$sum": 1},
                        }
                    },
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
        else:
            pipeline = [
                {"$match": {"authors.affiliations.id": ObjectId(idx)}},
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
        if result:
            return {"plot": result}
        else:
            return {"plot": None}

    def get_coauthorships_colombiamap(self, idx, typ=None, aff_type: str | None = None):
        data = []
        if typ in ["group", "department", "faculty"]:
            for author in self.colav_db["person"].find(
                {"affiliations.id": ObjectId(idx)}, {"affiliations": 1}
            ):
                pipeline = [
                    {"$match": {"authors.id": author["_id"]}},
                    {"$unwind": "$authors"},
                    {
                        "$group": {
                            "_id": "$authors.affiliations.id",
                            "count": {"$sum": 1},
                        }
                    },
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
        else:
            pipeline = [
                {"$match": {"authors.affiliations.id": ObjectId(idx)}},
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

    def get_coauthorships_network(self, idx, typ=None, aff_type: str | None = None):
        if typ in ["group", "department", "faculty"]:
            return {"plot": None}
        data = self.impactu_db["affiliations"].find_one(
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
    def plot_mappings(self) -> dict[str, Callable[[Any, Any], dict[str, list] | None]]:
        return {
            "year_type": self.get_products_by_year_by_type,
            "type,faculty": self.get_products_by_affiliation_by_type,
            "type,department": self.get_products_by_affiliation_by_type,
            "type,group": self.get_products_by_affiliation_by_type,
            "year_citations": self.get_citations_by_year,
            "year_apc": self.get_apc_by_year,
            "year_oa": self.get_oa_by_year,
            "year_publisher": self.get_products_by_year_by_publisher,
            "year_h": self.get_h_by_year,
            "year_researcher": self.get_products_by_year_by_researcher_category,
            "year_group": self.get_products_by_year_by_group_category,
            "title_words": self.get_title_words,
            "citations,faculty": self.get_citations_by_affiliations,
            "citations,department": self.get_citations_by_affiliations,
            "citations,group": self.get_citations_by_affiliations,
            "products,faculty": self.get_products_by_affiliations,
            "products,department": self.get_products_by_affiliations,
            "products,group": self.get_products_by_affiliations,
            "apc,faculty": self.get_apc_by_affiliations,
            "apc,department": self.get_apc_by_affiliations,
            "apc,group": self.get_apc_by_affiliations,
            "h,faculty": self.get_h_by_affiliations,
            "h,department": self.get_h_by_affiliations,
            "h,group": self.get_h_by_affiliations,
            "products_publisher": self.get_products_by_publisher,
            "products_subject": self.get_products_by_subject,
            "products_database": self.get_products_by_database,
            "products_oa": self.get_products_by_open_access_status,
            "products_sex": self.get_products_by_author_sex,
            "products_age": self.get_products_by_author_age,
            "scienti_rank": self.get_products_by_scienti_rank,
            "scimago_rank": self.get_products_by_scimago_rank,
            "published_institution": self.get_publisher_same_institution,
            "collaboration_worldmap": self.get_coauthorships_worldmap,
            "collaboration_colombiamap": self.get_coauthorships_colombiamap,
            "collaboration_network": self.get_coauthorships_network,
        }


affiliation_app_service = AffiliationAppService()

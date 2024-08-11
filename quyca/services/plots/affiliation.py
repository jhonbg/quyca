from itertools import chain

# Resolver esta dependencia
from bson import ObjectId
from pymongo import MongoClient

from protocols.mongo.repositories.work import WorkRepository
from protocols.mongo.repositories.affiliation import AffiliationRepository
from core.config import settings
from core.logging import get_logger
from utils.bars import bars
from utils.maps import maps
from utils.pies import pies
from utils.mapping import get_openalex_scienti

client = MongoClient(host=str(settings.MONGO_URI))
log = get_logger(__name__)


class AffiliationPlotsService:
    def __init__(
        self,
        work_repository: WorkRepository = None,
        affiliation_repository: AffiliationRepository = None,
    ):
        self.work_repository = work_repository
        self.affiliation_repository = affiliation_repository
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]
        self.bars = bars()
        self.pies = pies()
        self.maps = maps()

    def register_work_observer(self, repository: WorkRepository):
        log.info("Registering work repository on affiliation plots service")
        self.work_repository = repository

    def register_affiliation_observer(self, repository: AffiliationRepository):
        log.info("Registering affiliation repository on affiliation plots service")
        self.affiliation_repository = repository

    def get_products_by_year_by_type(self, idx, typ=None, aff_type: str | None = None):
        data, f = self.work_repository.get_research_products_by_affiliation(
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
        data, f = self.work_repository.get_research_products_by_affiliation(
            idx,
            aff_type,
            available_filters=False,
            project=["citations_by_year", "year_published"],
        )
        return {"plot": self.bars.citations_by_year(data)}

    def get_apc_by_year(self, idx, typ=None, aff_type: str | None = None):
        sources = self.work_repository.get_sources_by_affiliation(
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
        data, f = self.work_repository.get_research_products_by_affiliation(
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
        sources = self.work_repository.get_sources_by_affiliation(
            idx,
            aff_type,
            match={"$and": [{"publisher": {"$exists": 1}}, {"publisher": {"$ne": ""}}]},
            project=["publisher", "apc"],
        )
        return {"plot": self.bars.products_by_year_by_publisher(sources)}

    def get_h_by_year(self, idx, typ=None, aff_type: str | None = None):
        _match = {"citations_by_year": {"$exists": 1}}
        works, f = self.work_repository.get_research_products_by_affiliation(
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
        groups = self.affiliation_repository.get_groups_by_affiliation(idx, aff_type)
        for group in groups:
            works, _ = self.work_repository.get_research_products_by_affiliation(
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

    def get_citations_by_affiliations(self, idx, typ, aff_type: str | None = None):
        if not typ in ["group", "department", "faculty"]:
            return None
        affiliations = self.affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        _data = {}
        for aff in affiliations:
            _data[aff.name] = self.work_repository.count_citations(
                affiliation_id=aff.id
            )
        return self.pies.citations_by_affiliation(_data)

    def get_products_by_affiliations(self, idx, typ, aff_type: str | None = None):
        affiliations = self.affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        data = {}
        for aff in affiliations:
            data[aff.name] = self.work_repository.count_papers(
                affiliation_id=aff.id, affiliation_type=aff.types[0].type
            )
        total_works = self.work_repository.count_papers(
            affiliation_id=idx, affiliation_type=aff_type
        )
        return self.pies.products_by_affiliation(data, total_works)

    def get_apc_by_affiliations(self, idx, typ, aff_type: str | None = None):
        sources = self.work_repository.get_sources_by_related_affiliations(
            idx,
            aff_type,
            typ,
            match={
                "$and": [
                    {"apc.charges": {"$exists": 1}},
                    {"apc.currency": {"$exists": 1}},
                ]
            },
            project=["apc", "affiliation_names"],
        )
        return self.pies.apc_by_affiliation(sources, 2022)

    def get_h_by_affiliations(self, idx, typ, aff_type: str | None = None):
        affiliations = self.affiliation_repository.get_affiliations_related_type(
            idx, typ, aff_type
        )
        _data = {}
        for aff in affiliations:
            works, _ = self.work_repository.get_research_products_by_affiliation(
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
        sources = self.work_repository.get_sources_by_affiliation(
            idx,
            aff_type,
            project=["publisher"],
        )
        data = map(
            lambda x: (
                x.publisher.name
                if x.publisher and isinstance(x.publisher.name, str)
                else "Sin información"
            ),
            sources,
        )
        return self.pies.products_by_publisher(data)

    def get_products_by_subject(
        self, idx, level: int = 0, typ: str = None, aff_type: str | None = None
    ):
        works, _ = self.work_repository.get_research_products_by_affiliation(
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
        works, _ = self.work_repository.get_research_products_by_affiliation(
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
        works, _ = self.work_repository.get_research_products_by_affiliation(
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
        pipeline = [
            {"$project": {"affiliations": 1, "sex": 1}},
            {"$match": {"affiliations.id": ObjectId(idx)}},
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "authors.id",
                    "as": "work",
                }
            },
            {"$unwind": "$work"},
            {
                "$addFields": {
                    "sex": {
                        "$cond": {
                            "if": {"$eq": ["$sex", ""]},
                            "then": "sin información",
                            "else": "$sex",
                        }
                    }
                }
            },
            {"$project": {"sex": 1}},
            {"$group": {"_id": "$sex", "count": {"$sum": 1}}},
            {"$project": {"name": "$_id", "_id": 0, "value": "$count"}},
        ]
        data = list(self.colav_db["person"].aggregate(pipeline))
        return self.pies.products_by_sex(data)

    def get_products_by_author_age(self, idx, typ=None, aff_type: str | None = None):
        pipeline = [
            {"$project": {"affiliations": 1, "birthdate": 1}},
            {"$match": {"affiliations.id": ObjectId(idx)}},
            {
                "$lookup": {
                    "from": "works",
                    "localField": "_id",
                    "foreignField": "authors.id",
                    "as": "work",
                }
            },
            {"$unwind": "$work"},
            {
                "$project": {
                    "birthdate": 1,
                    "work.date_published": 1,
                    "work.year_published": 1,
                }
            },
        ]
        data = self.colav_db["person"].aggregate(pipeline)
        result = self.pies.products_by_age(data)
        if result:
            return result
        else:
            return {"plot": None}

    def get_products_by_scienti_rank(self, idx, typ=None, aff_type: str | None = None):
        works, _ = self.work_repository.get_research_products_by_affiliation(
            idx,
            aff_type,
            match={"ranking": {"$ne": []}},
            available_filters=False,
            project=["ranking"],
        )
        total_works = self.work_repository.count_papers(
            affiliation_id=idx, affiliation_type=aff_type
        )
        _data = chain.from_iterable(map(lambda x: x.ranking, works))
        return self.pies.products_by_scienti_rank(_data, total_works)

    def get_products_by_scimago_rank(self, idx, typ=None, aff_type: str | None = None):
        sources = self.work_repository.get_sources_by_affiliation(
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
        sources = self.work_repository.get_sources_by_affiliation(
            idx, aff_type, project=["publisher"]
        )
        return self.pies.products_editorial_same_institution(sources, institution)

    def get_coauthorships_worldmap(self, affiliation_id, affiliation_type, tab=None):
        data = []

        if affiliation_type in ["group", "department", "faculty"]:
            institution_id = self.colav_db["affiliations"].aggregate([
                {
                    '$match': {
                        '_id': ObjectId('665e0b3daa7c2077adf68220')
                    }
                }, {
                    '$unwind': '$relations'
                }, {
                    '$match': {
                        'relations.types.type': 'Education'
                    }
                }
            ]).next().get("relations", [])["id"]

            pipeline = [
                {
                    '$match': {
                        'affiliations.id': ObjectId(affiliation_id)
                    }
                }, {
                    '$project': {
                        '_id': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'works',
                        'localField': '_id',
                        'foreignField': 'authors.id',
                        'as': 'work',
                        'pipeline': [
                            {
                                '$project': {
                                    '_id': 1,
                                    'authors': 1
                                }
                            }
                        ]
                    }
                }, {
                    '$unwind': '$work'
                }, {
                    '$match': {
                        'work.authors.affiliations.id': institution_id
                    }
                }, {
                    '$unwind': '$work.authors'
                }, {
                    '$unwind': '$work.authors.affiliations'
                }, {
                    '$group': {
                        '_id': '$work.authors.affiliations.id',
                        'count': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$lookup': {
                        'from': 'affiliations',
                        'localField': '_id',
                        'foreignField': '_id',
                        'as': 'affiliation',
                        'pipeline': [
                            {
                                '$project': {
                                    'addresses.country_code': 1,
                                    'addresses.country': 1
                                }
                            }
                        ]
                    }
                }, {
                    '$unwind': '$affiliation'
                }, {
                    '$unwind': '$affiliation.addresses'
                }
            ]

            for person in self.colav_db["person"].aggregate(pipeline):
                data.append(person)
        else:
            pipeline = [
                {
                    '$match': {
                        'authors.affiliations.id': ObjectId(affiliation_id)
                    }
                }, {
                    '$unwind': '$authors'
                }, {
                    '$unwind': '$authors.affiliations'
                }, {
                    '$group': {
                        '_id': '$authors.affiliations.id',
                        'count': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$lookup': {
                        'from': 'affiliations',
                        'localField': '_id',
                        'foreignField': '_id',
                        'as': 'affiliation',
                        'pipeline': [
                            {
                                '$project': {
                                    'addresses.country_code': 1,
                                    'addresses.country': 1
                                }
                            }
                        ]
                    }
                }, {
                    '$unwind': '$affiliation'
                }, {
                    '$unwind': '$affiliation.addresses'
                }
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
        pipeline = [
            {"$match": {"_id": ObjectId(idx)}},
            {"$project": {"coauthorship_network": 1}},
            {
                "$lookup": {
                    "from": "affiliations_edges",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "complement",
                }
            },
            {"$unwind": "$complement"},
            {
                "$project": {
                    "coauthorship_network": {
                        "nodes": "$coauthorship_network.nodes",
                        "edges": {
                            "$concatArrays": [
                                "$coauthorship_network.edges",
                                "$complement.coauthorship_network.edges",
                            ]
                        },
                    }
                }
            },
        ]
        data = self.impactu_db["affiliations"].aggregate(pipeline)
        if next(data):
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


affiliation_plots_service = AffiliationPlotsService()

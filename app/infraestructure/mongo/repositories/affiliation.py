from typing import Any, Iterable

from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import Affiliation
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine
from infraestructure.mongo.utils.iterators import AffiliationIterator
from schemas.affiliation import AffiliationRelated
from schemas.person import PersonList


class AffiliationRepository(RepositoryBase):
    def get_affiliations_related_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> list[AffiliationRelated]:
        if affiliation_type in ["department", "faculty"] and relation_type == "group":
            groups = self.get_groups_by_affiliation(idx, affiliation_type)
            return [AffiliationRelated(**group.model_dump()) for group in groups]
        results = engine.get_collection(Affiliation).find(
            {"relations.id": ObjectId(idx), "types.type": relation_type}
        )
        return [
            AffiliationRelated.model_validate_json(
                Affiliation(**result).model_dump_json(exclude={"id"})[:-1]
                + ', "id":"'
                + str(result.get("_id", "None"))
                + '"}'
            )
            for result in results
        ]

    def get_groups_by_affiliation(self, idx: str, typ: str) -> Iterable[Affiliation]:
        if typ == "group":
            with engine.session() as session:
                affiliation = session.find_one(
                    Affiliation, Affiliation.id == ObjectId(idx)
                )
                return [affiliation]
        if typ in ["department", "faculty"]:
            group_pipeline = [
                {"$match": {"affiliations.id": ObjectId(idx)}},
                {"$project": {"affiliations": 1}},
                {"$unwind": "$affiliations"},
                {"$match": {"affiliations.types.type": "group"}},
                {"$project": {"aff_id": "$affiliations.id"}},
                {
                    "$lookup": {
                        "from": "affiliations",
                        "localField": "aff_id",
                        "foreignField": "_id",
                        "as": "affiliation",
                    }
                },
                {"$unwind": "$affiliation"},
                {
                    "$group": {
                        "_id": "$aff_id",
                        "affiliation": {"$addToSet": "$affiliation"},
                    }
                },
                {"$unwind": "$affiliation"},
                {"$project": {"_id": 0, "affiliation": 1}},
                {"$replaceRoot": {"newRoot": "$affiliation"}},
            ]
            groups = engine.get_collection(Person).aggregate(group_pipeline)
            return AffiliationIterator(groups)
        groups = engine.get_collection(Affiliation).find(
            {"relations.id": ObjectId(idx), "types.type": typ}
        )
        return AffiliationIterator(groups)

    def get_authors_by_affiliation(self, idx: str, typ: str) -> list[Person]:
        pipeline = [
            {"$match": {"affiliations.id": ObjectId(idx)}},
            {"$project": {"full_name": 1}},
        ]
        authors = engine.get_collection(Person).aggregate(pipeline)
        return [
            PersonList(id=str(author["_id"]), full_name=author["full_name"])
            for author in authors
        ]

    @classmethod
    def upside_relations(
        cls, relations: list[dict, str], typ: str
    ) -> list[dict[str, Any]]:
        hierarchy = ["group", "department", "faculty", "Education", "institution"]
        upside = hierarchy.index(typ)
        affiliations = list(
            filter(
                lambda x: x["types"][0]["type"] in hierarchy
                and hierarchy.index(x["types"][0]["type"]) > upside,
                relations,
            )
        )
        affiliations_result = []
        for affiliation in affiliations:
            id = (
                affiliation["id"]
                if isinstance(affiliation["id"], ObjectId)
                else ObjectId(affiliation["id"])
            )
            affiliation = engine.get_collection(Affiliation).find_one(
                {"_id": id}, {"names": 1, "types": 1}
            )
            if affiliation:
                affiliations_result.append(
                    {
                        "id": str(affiliation["_id"]),
                        "name": next(
                            filter(lambda x: x["lang"] == "es", affiliation["names"]),
                            affiliation["names"][0],
                        )["name"],
                        "types": affiliation["types"],
                    }
                )
        return affiliations_result

    def get_products(
        self,
        *,
        affiliation_id: int,
        affiliation_type: str,
        skip: int = 0,
        limit: int = 100
    ): ...


affiliation_repository = AffiliationRepository(Affiliation)

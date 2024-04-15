from bson import ObjectId

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import Affiliation
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine
from schemas.affiliation import AffiliationRelated
from schemas.person import PersonList


class AffiliationRepository(RepositoryBase):
    def get_affiliations_related_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> list[AffiliationRelated]:
        if affiliation_type in ["department", "faculty"] and relation_type == "group":
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
            return [
                AffiliationRelated.model_validate_json(
                    Affiliation(**group).model_dump_json(exclude={"id"})[:-1]
                    + ', "id":"'
                    + str(group.get("_id", "None"))
                    + '"}'
                )
                for group in groups
            ]
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


affiliation_repository = AffiliationRepository(Affiliation)

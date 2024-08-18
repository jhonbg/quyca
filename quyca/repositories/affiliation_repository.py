from typing import Generator

from bson import ObjectId

from generators.affiliation_generator import AffiliationGenerator
from repositories.mongo import database


class AffiliationRepository:
    @classmethod
    def get_groups_by_affiliation(cls, affiliation_id: str, affiliation_type: str):
        pipeline = cls.get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)
        collection = "person" if affiliation_type in ["faculty", "department"] else "affiliations"
        groups = database[collection].aggregate(pipeline)

        return AffiliationGenerator.get(groups)


    @staticmethod
    def get_groups_by_affiliation_pipeline(affiliation_id: str, affiliation_type: str) -> list:
            if affiliation_type == "group":
                return [{"$match": {"_id": ObjectId(affiliation_id)}}]

            if affiliation_type in ["department", "faculty"]:
                return [
                    {"$match": {"affiliations.id": ObjectId(affiliation_id)}},
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
            return [
                {
                    "$match": {
                        "relations.id": ObjectId(affiliation_id),
                        "types.type": "group",
                    }
                }
            ]


    @classmethod
    def get_related_affiliations_by_type(cls, affiliation_id: str, relation_type: str) -> Generator:
            pipeline = cls.get_related_affiliations_by_type_pipeline(affiliation_id, relation_type)
            affiliations = database["affiliations"].aggregate(pipeline)

            return AffiliationGenerator.get(affiliations)


    @staticmethod
    def get_related_affiliations_by_type_pipeline(affiliation_id: str, relation_type: str) -> list:
        if relation_type == "group":
            return [
                {"$match": {"_id": ObjectId(affiliation_id)}}
            ]

        return [
            {
                "$match": {
                    "relations.id": ObjectId(affiliation_id),
                    "types.type": relation_type,
                }
            }
        ]
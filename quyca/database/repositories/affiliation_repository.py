from typing import Generator

from bson import ObjectId

from core.config import settings
from exceptions.affiliation_exception import AffiliationException
from database.generators import affiliation_generator
from database.models.affiliation_model import Affiliation
from database.repositories.calculations_repository import CalculationsRepository
from database.mongo import database


class AffiliationRepository:
    @classmethod
    def get_affiliation_by_id(cls, affiliation_id: str) -> Affiliation:
        from database.repositories.work_repository import WorkRepository

        affiliation_data = database["affiliations"].find_one({"_id": ObjectId(affiliation_id)})

        if not affiliation_data:
            raise AffiliationException(affiliation_id)

        affiliation = Affiliation(**affiliation_data)

        upper_affiliations, logo = cls.get_upper_affiliations(
            [relation.model_dump() for relation in affiliation.relations], affiliation.types[0].type
        )

        affiliation_calculations = CalculationsRepository.get_affiliation_calculations(affiliation_id)

        affiliation.citations_count = affiliation_calculations.citations_count
        affiliation.products_count = WorkRepository.get_works_count_by_affiliation(affiliation_id, affiliation.types[0].type)
        affiliation.affiliations = upper_affiliations

        if logo:
            affiliation.logo = logo

        return affiliation


    @staticmethod
    def get_upper_affiliations(affiliations: list, affiliation_type: str) -> tuple[list, str]:
        affiliations_hierarchy = ["group", "department", "faculty"] + settings.institutions
        affiliation_position = affiliations_hierarchy.index(affiliation_type)

        affiliations = list(
            filter(
                lambda x: x["types"][0]["type"] in affiliations_hierarchy
                and affiliations_hierarchy.index(x["types"][0]["type"]) > affiliation_position,
                affiliations,
            )
        )

        logo = ""
        upper_affiliations = []

        for affiliation in affiliations:
            affiliation_id = (
                affiliation["id"] if isinstance(affiliation["id"], ObjectId) else ObjectId(affiliation["id"])
            )

            affiliation = database["affiliations"].find_one(
                {"_id": affiliation_id}, {"names": 1, "types": 1, "external_urls": 1}
            )

            if affiliation:
                if affiliation["types"][0]["type"] in settings.institutions:
                    for external_url in affiliation["external_urls"]:
                        if external_url["source"] == "logo":
                            logo = external_url["url"]

                upper_affiliations.append(
                    {
                        "id": str(affiliation["_id"]),
                        "name": next(
                            filter(lambda name: name["lang"] == "es", affiliation["names"]),
                            affiliation["names"][0]
                        )["name"],
                        "types": affiliation["types"],
                    }
                )

        return upper_affiliations, logo

    @classmethod
    def get_groups_by_affiliation(cls, affiliation_id: str, affiliation_type: str):
        pipeline = cls.get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)
        collection = "person" if affiliation_type in ["faculty", "department"] else "affiliations"
        groups = database[collection].aggregate(pipeline)

        return affiliation_generator.get(groups)


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
    def get_related_affiliations_by_type(
            cls, affiliation_id: str, affiliation_type: str, relation_type: str
    ) -> Generator:
            pipeline = cls.get_related_affiliations_by_type_pipeline(affiliation_id, affiliation_type, relation_type)
            affiliations = database["affiliations"].aggregate(pipeline)

            return affiliation_generator.get(affiliations)


    @classmethod
    def get_related_affiliations_by_type_pipeline(
            cls, affiliation_id: str, affiliation_type: str, relation_type: str
    ) -> list:
        if relation_type == "group":
            return cls.get_groups_by_affiliation_pipeline(affiliation_id, affiliation_type)

        return [
            {
                "$match": {
                    "relations.id": ObjectId(affiliation_id),
                    "types.type": relation_type,
                }
            }
        ]
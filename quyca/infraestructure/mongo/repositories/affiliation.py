from typing import Any, Iterable

from bson import ObjectId
from odmantic import Model

from infraestructure.mongo.repositories.base import RepositoryBase
from infraestructure.mongo.models.affiliation import Affiliation
from infraestructure.mongo.models.person import Person
from infraestructure.mongo.utils.session import engine
from infraestructure.mongo.utils.iterators import AffiliationIterator
from schemas.affiliation import AffiliationRelated
from schemas.person import PersonList
from core.config import settings


class AffiliationRepository(RepositoryBase[Affiliation, AffiliationIterator]):
    def __groups_by_affiliation(
        self, idx: str, typ: str
    ) -> tuple[list[dict[str, Any]], Model]:
        """
        Retrieve groups by affiliation.

        Args:
            idx (str): The ID of the affiliation.
            typ (str): The type of affiliation.

        Returns:
            tuple[list[dict[str, Any]], Model]: A tuple containing the aggregation pipeline and the model.

        Raises:
            None.

        """
        if typ == "group":
            return [{"$match": {"_id": ObjectId(idx)}}], Affiliation
        if typ in ["department", "faculty"]:
            return [
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
            ], Person
        return [
            {
                "$match": {
                    "relations.id": ObjectId(idx),
                    "types.type": "group",
                }
            }
        ], Affiliation

    def related_affiliations_by_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> tuple[list[dict[str, Any]], Model]:
        """
        Retrieve related affiliations based on the given relation type and affiliation type.

        Args:
            idx (str): The ID of the affiliation.
            relation_type (str): The type of relation.
            affiliation_type (str): The type of affiliation.

        Returns:
            tuple[list[dict[str, Any]], Model]: A tuple containing a list of MongoDB aggregation pipeline stages
            and the Affiliation model.

        Raises:
            None

        """
        if relation_type == "group":
            return self.__groups_by_affiliation(idx, affiliation_type)
        return [
            {
                "$match": {
                    "relations.id": ObjectId(idx),
                    "types.type": relation_type,
                }
            }
        ], Affiliation

    def get_affiliations_related_type(
        self, idx: str, relation_type: str, affiliation_type: str
    ) -> Iterable[AffiliationRelated]:
        """
        Retrieves affiliations related to a specific type.

        Args:
            idx (str): The index of the affiliation.
            relation_type (str): The relation type of the affiliation.
            affiliation_type (str): The type of the affiliation.

        Returns:
            Iterable[AffiliationRelated]: An iterable of AffiliationRelated objects.

        """
        pipeline, collection = self.related_affiliations_by_type(
            idx, relation_type, affiliation_type
        )
        results = engine.get_collection(collection).aggregate(pipeline)
        return map(
            lambda x: AffiliationRelated.model_validate_json(x.model_dump_json()),
            AffiliationIterator(results),
        )

    def get_groups_by_affiliation(self, idx: str, typ: str) -> Iterable[Affiliation]:
        """
        Retrieves groups by affiliation based on the given index and type.

        Args:
            idx (str): The index of the affiliation.
            typ (str): The type of the affiliation.

        Returns:
            Iterable[Affiliation]: An iterable of Affiliation objects.

        Raises:
            None

        """
        group_pipeline, collection = self.__groups_by_affiliation(idx, typ)
        groups = engine.get_collection(collection).aggregate(group_pipeline)
        return AffiliationIterator(groups)

    def get_authors_by_affiliation(self, idx: str, typ: str) -> list[Person]:
        """
        Retrieve a list of authors associated with a specific affiliation.

        Args:
            idx (str): The ID of the affiliation.
            typ (str): The type of the affiliation.

        Returns:
            list[Person]: A list of Person objects representing the authors.

        """
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
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Retrieve the upside relations of a given type.

        This method filters the given relations based on their types and returns the upside relations
        that are higher in the hierarchy than the given type.

        Args:
            relations (list[dict, str]): The list of relations to filter.
            typ (str): The type to compare against.

        Returns:
            tuple[list[dict[str, Any]], str]: A tuple containing the filtered upside relations and the logo URL.

        """
        hierarchy = ["group", "department", "faculty"] + settings.institutions
        upside = hierarchy.index(typ)
        affiliations = list(
            filter(
                lambda x: x["types"][0]["type"] in hierarchy
                and hierarchy.index(x["types"][0]["type"]) > upside,
                relations,
            )
        )
        logo = ""
        affiliations_result = []
        for affiliation in affiliations:
            id = (
                affiliation["id"]
                if isinstance(affiliation["id"], ObjectId)
                else ObjectId(affiliation["id"])
            )
            affiliation = engine.get_collection(Affiliation).find_one(
                {"_id": id}, {"names": 1, "types": 1, "external_urls": 1}
            )
            if affiliation:
                if affiliation["types"][0]["type"] in settings.institutions:
                    for ext in affiliation["external_urls"]:
                        if ext["source"] == "logo":
                            logo = ext["url"]
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
        return affiliations_result, logo

    def get_products(
        self,
        *,
        affiliation_id: int,
        affiliation_type: str,
        skip: int = 0,
        limit: int = 100
    ):
        ...


affiliation_repository = AffiliationRepository(
    Affiliation, iterator=AffiliationIterator
)

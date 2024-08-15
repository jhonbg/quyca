from typing import Optional

from bson import ObjectId

from repositories.mongo import database


class WorkRepository:
    work_collection = database["works"]

    @staticmethod
    def get_works_count_by_person_id(person_id) -> Optional[int]:
        return WorkRepository.work_collection.aggregate([
            {"$match": {"authors.id": ObjectId(person_id)}},
            {"$count": "total"}
        ]).next().get("total", 0)
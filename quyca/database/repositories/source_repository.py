from bson import ObjectId

from database.models.source_model import Source
from database.mongo import database
from exceptions.not_entity_exception import NotEntityException


def get_source_by_id(source_id: str) -> Source:
    source_data = database["sources"].find_one({"_id": ObjectId(source_id)})
    if not source_data:
        raise NotEntityException(f"The source with id {source_id} does not exist.")
    return Source(**source_data)

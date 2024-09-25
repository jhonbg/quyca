from bson import ObjectId

from domain.models.source_model import Source
from infrastructure.mongo import database
from domain.exceptions.not_entity_exception import NotEntityException


def get_source_by_id(source_id: str) -> Source:
    source_data = database["sources"].find_one({"_id": ObjectId(source_id)})
    if not source_data:
        raise NotEntityException(f"The source with id {source_id} does not exist.")
    return Source(**source_data)

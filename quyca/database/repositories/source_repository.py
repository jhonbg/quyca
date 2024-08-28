from bson import ObjectId

from database.models.source_model import Source
from database.mongo import database
from exceptions.source_exception import SourceException


def get_source_by_id(source_id: str) -> Source:
    source_data = database["sources"].find_one({"_id": ObjectId(source_id)})
    if not source_data:
        raise SourceException(source_id)
    return Source(**source_data)

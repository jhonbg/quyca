from quyca.domain.constants.institutions import institutions_list
from quyca.infrastructure.mongo import database


def get_last_db_update() -> int:
    pipeline = [{"$group": {"_id": None, "max_time": {"$max": "$time"}}}]
    return next(database["log"].aggregate(pipeline), {"max_time": 0}).get("max_time", 0)


def get_entity_count(entity: str, affiliation_type: str | None = None) -> int:
    if affiliation_type:
        if affiliation_type == "institution":
            return database[entity].count_documents({"types.type": {"$in": institutions_list}})
        return database[entity].count_documents({"types.type": affiliation_type})
    return database[entity].count_documents({})

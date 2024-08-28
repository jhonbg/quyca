from odmantic.engine import SyncEngine
from pymongo import MongoClient

from core.config import settings

client = MongoClient(host=str(settings.MONGO_URI))

engine = SyncEngine(client=client, database=settings.MONGO_DATABASE)

client_calculations = MongoClient(host=str(settings.MONGO_URI))
engine_calculations = SyncEngine(
    client=client_calculations, database=settings.MONGO_CALCULATIONS_DATABASE
)

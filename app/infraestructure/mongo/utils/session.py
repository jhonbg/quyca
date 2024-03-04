from odmantic.engine import SyncEngine
from pymongo import MongoClient

from core.config import settings

client = MongoClient(host=str(settings.MONGO_URI))

engine = SyncEngine(client=client, database=settings.MONGO_INITDB_DATABASE)
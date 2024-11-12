from pymongo import MongoClient
from pymongo.database import Database

from config import settings

database: Database = MongoClient(host=str(settings.MONGO_URI))[settings.MONGO_DATABASE]
calculations_database: Database = MongoClient(host=str(settings.MONGO_URI))[settings.MONGO_CALCULATIONS_DATABASE]

from pymongo import MongoClient

from core.config import settings

database = MongoClient(host=str(settings.MONGO_URI))[settings.MONGO_DATABASE]
calculations_database = MongoClient(host=str(settings.MONGO_URI))[
    settings.MONGO_CALCULATIONS_DATABASE
]

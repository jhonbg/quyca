from infraestructure.mongo.utils.session import client
from core.config import settings


class OurDataAppService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]

    def get_our_data(self):
        entry = {
            "works": self.colav_db["works"].count_documents({}),
            "authors": self.colav_db["person"].count_documents(
                {"external_ids": {"$ne": []}}
            ),
            "affiliations": self.colav_db["affiliations"].count_documents(
                {"external_ids": {"$ne": []}}
            ),
            "sources": self.colav_db["sources"].count_documents({}),
        }
        return entry
    

our_data_app_service = OurDataAppService()
from pymongo.cursor import Cursor

from database.models.affiliation_model import Affiliation


def get(cursor: Cursor):
   for document in cursor:
       yield Affiliation(**document)
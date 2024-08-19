from pymongo.cursor import Cursor

from database.models.affiliation_model import Affiliation


class AffiliationGenerator:
   @staticmethod
   def get(cursor: Cursor):
       for document in cursor:
           yield Affiliation(**document)
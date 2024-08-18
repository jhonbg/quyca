from pymongo.cursor import Cursor

from models.source_model import Source


class SourceGenerator:
   @staticmethod
   def get(cursor: Cursor):
       for document in cursor:
           yield Source(**document)
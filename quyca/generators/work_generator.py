from pymongo.cursor import Cursor

from models.work_model import Work


class WorkGenerator:
   @staticmethod
   def get(cursor: Cursor):
       for document in cursor:
           yield Work(**document)
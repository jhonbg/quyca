from pymongo.cursor import Cursor

from database.models.person_model import Person


def get(cursor: Cursor):
   for document in cursor:
       yield Person(**document)
from pymongo.command_cursor import CommandCursor

from database.models.person_model import Person


def get(cursor: CommandCursor):
    for document in cursor:
        yield Person(**document)

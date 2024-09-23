from typing import Generator

from pymongo.command_cursor import CommandCursor

from database.models.other_work_model import OtherWork


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield OtherWork(**document)

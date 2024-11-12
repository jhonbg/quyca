from typing import Generator

from pymongo.command_cursor import CommandCursor

from domain.models.affiliation_model import Affiliation


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Affiliation(**document)

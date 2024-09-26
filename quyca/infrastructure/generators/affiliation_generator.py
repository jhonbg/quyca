from typing import Generator

from pymongo.command_cursor import CommandCursor

from domain.models.affiliation_model import Affiliation
from domain.models.base_model import Affiliation as EntityAffiliation


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield Affiliation(**document)


def get_entity_affiliations(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield EntityAffiliation(**document)

from typing import Generator
from pymongo.command_cursor import CommandCursor
from domain.models.news_model import News


def get(cursor: CommandCursor) -> Generator:
    for document in cursor:
        yield News(**document)

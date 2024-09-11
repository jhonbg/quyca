from typing import Generic, TypeVar, Any, Literal, Iterable
from json import loads

from odmantic import Model, ObjectId
from odmantic.engine import SyncEngine
from odmantic.query import desc, asc

from infraestructure.mongo.utils.session import engine
from infraestructure.mongo.utils.iterators import CollectionIterator

ModelType = TypeVar("ModelType", bound=Model)
IteratorType = TypeVar("IteratorType", bound=CollectionIterator)


class RepositoryBase(Generic[ModelType, IteratorType]):
    def __init__(
        self,
        model: type[ModelType],
        iterator: type[IteratorType] = None,
        engine: SyncEngine = engine,
    ):
        self.model = model
        self.iterator = iterator
        self.engine = engine

    def get_all(
        self, *, query: dict[str, Any], skip: int = 0, limit: int = 10, sort: str = None
    ) -> list[ModelType]:
        """
        Retrieve a list of models from the database based on the provided query.

        Args:
            query (dict[str, Any]): The query to filter the models.
            skip (int, optional): The number of models to skip. Defaults to 0.
            limit (int, optional): The maximum number of models to retrieve. Defaults to 10.
            sort (str, optional): The field to sort the models. Defaults to None.

        Returns:
            list[ModelType]: A list of models matching the query.
        """
        with self.engine.session() as session:
            results = session.find(
                self.model,
                **{getattr(self.model, k): v for k, v in query.items()},
                skip=skip,
                limit=limit,
                sort=getattr(self.model, sort, None),
            )
        return [loads(result.model_dump_json()) for result in results]

    def get_by_id(self, *, id: str) -> str | None:
        """
        Retrieve a document from the database by its ID.

        Args:
            id (str): The ID of the document to retrieve.

        Returns:
            str | None: The JSON representation of the retrieved document, or None if not found.
        """
        with self.engine.session() as session:
            results = session.find_one(self.model, self.model.id == ObjectId(id))
        return results.model_dump_json() if results else None

    def search(
        self,
        *,
        keywords: str = "",
        skip: int = 0,
        limit: int = 10,
        sort: str = "",
        search: dict[str, Any] = {}
    ) -> tuple[Iterable[ModelType], int]:
        """
        Search for documents in the collection based on the provided criteria.

        Args:
            keywords (str): Keywords to search for in the documents.
            skip (int): Number of documents to skip in the result.
            limit (int): Maximum number of documents to return.
            sort (str): Field to sort the documents by.
            search (dict[str, Any]): Additional search criteria.

        Returns:
            tuple[Iterable[ModelType], int]: A tuple containing the matching documents and the total count.

        """
        filter_criteria = search
        projection = None
        sort_expresion = [("$natural", 1)]
        if keywords:
            filter_criteria["$text"] = {"$search": keywords}
            projection = {"score": {"$meta": "textScore"}}
            sort_expresion = [("score", {"$meta": "textScore"})]
        # if sort:
        #     projection = None
        #     sort_expresion = (
        #         desc(getattr(self.model, sort[:-1]))
        #         if sort.endswith("-")
        #         else asc(getattr(self.model, sort))
        #     )
        session = self.engine.get_collection(self.model)
        results = (
            session.find(filter_criteria, projection)
            .sort(sort_expresion)
            .skip(skip)
            .limit(limit)
        )
        count = session.count_documents(filter_criteria)
        return self.iterator(results), count

    def count(self) -> int:
        """
        Returns the number of documents in the collection.

        :return: The count of documents in the collection.
        :rtype: int
        """
        with self.engine.session() as session:
            return session.count(self.model)

    def aggregate(self, pipeline: list[dict[str, Any]]) -> Iterable[ModelType]:
        results = self.engine.get_collection(self.model).aggregate(pipeline)
        return self.iterator(results)

    @staticmethod
    def get_sort_direction(sort: str) -> tuple[str, Literal[1, -1]]:
        """
        Get the sort field and direction based on the given sort string.

        Args:
            sort (str): The sort string indicating the field and direction.

        Returns:
            tuple[str, Literal[1, -1]]: A tuple containing the sort field and direction.
                The sort field is a string and the direction is either 1 (ascending) or -1 (descending).
        """
        if sort.endswith("-"):
            sort_field = sort[:-1]
            direction_value = -1
        else:
            sort_field = sort
            direction_value = 1
        return sort_field, direction_value

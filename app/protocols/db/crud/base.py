from datetime import date
from typing import Protocol, Generic, TypeVar, Any

from app.schemas.model import CreateSchemaType, UpdateSchemaType


ModelType = TypeVar("ModelType")


class CRUDProtocol(Protocol[ModelType, CreateSchemaType, UpdateSchemaType]):
    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        ...

    def get(self, *, id: int) -> ModelType:
        ...
        
    def get_multi(
        self,
        *,
        payload: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 10,
        order_by: str | None = None,
        date_range: dict[str, date] | None = None,
        values: tuple[str] | None = None
    ) -> list[ModelType | dict[str, Any]]:
        ...

    def update(self, *, id: int, obj_in: UpdateSchemaType) -> ModelType:
        ...

    def delete(self, *, id: int) -> int:
        ...
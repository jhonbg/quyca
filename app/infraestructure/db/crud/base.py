from typing import Generic, TypeVar, Any
from datetime import date

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ORMError
from app.infraestructure.db.utils.model import BaseModel as Model
from app.schemas.model import UpdateSchemaType, CreateSchemaType
from app.infraestructure.db.utils.session import SessionLocal


ModelType = TypeVar("ModelType", bound=Model)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: ModelType):
        self.model = model

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        with SessionLocal() as db:
            try:
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
            except IntegrityError as e:
                raise ORMError(str(e))

    def get(self, *, id: int) -> ModelType:
        with SessionLocal() as db:
            return db.query(self.model).filter(self.model.id == id).first()

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
        with SessionLocal() as db:
            try:
                return db.query(self.model).offset(skip).limit(limit).all()
            except IntegrityError as e:
                raise ORMError(str(e))

    def update(self, *, id: int, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        with SessionLocal() as db:
            try:
                db_obj = db.query(self.model).filter(self.model.id == id).first()
                for field in dict(db_obj):
                    if field in obj_data:
                        setattr(db_obj, field, obj_data[field])
                db.add(db_obj)
                db.commit()
                db.refresh(db_obj)
                return db_obj
            except IntegrityError as e:
                raise ORMError(str(e))

    def delete(self, *, id: int) -> int:
        with SessionLocal() as db:
            try:
                obj_db = db.query(self.model).get(id)
                db.delete(obj_db)
                db.commit()
                return True
            except IntegrityError as e:
                raise ORMError(str(e))

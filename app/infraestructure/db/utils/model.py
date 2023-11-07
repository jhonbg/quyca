from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseModel:
    id = Column(Integer, primary_key=True)
    __name__: str

    @declared_attr
    def __tablename__(cls):
        return cls._camel2snake(cls.__name__)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())

    def _camel2snake(name: str):
        return name[0].lower() + "".join(["_" + i.lower() 
            if i.isupper() else i for i in name[1:]]).lstrip("_")

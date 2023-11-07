from sqlalchemy import Column, String, Integer

from app.infraestructure.db.utils.model import BaseModel


class Buyer(BaseModel):
    email = Column(String(100), unique=True)
    names = Column(String(100), nullable=True)
    last_names = Column(String(100), nullable=True)
    address = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
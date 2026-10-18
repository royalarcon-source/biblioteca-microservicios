"""Patrón Repository genérico: aísla el acceso a datos de la lógica HTTP."""
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class Repository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def list(self, skip: int = 0, limit: int = 50) -> list[ModelT]:
        return list(self.db.scalars(select(self.model).offset(skip).limit(limit)))

    def get(self, obj_id: int) -> ModelT | None:
        return self.db.get(self.model, obj_id)

    def create(self, data: dict) -> ModelT:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelT, data: dict) -> ModelT:
        for key, value in data.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()

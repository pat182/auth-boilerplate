from abc import ABC, abstractmethod
from typing import Tuple, List
from sqlalchemy.orm import Session,Query

class BaseRepo(ABC):
    def __init__(self, db: Session):
        self.db = db

    @property
    @abstractmethod
    def model(self):
        pass
    def apply_search(self, query, search: str | None) -> Query:
        return query

    def get_by_id(self,uuid:str|int):
        return self.db.query(self.model).filter(self.model.id == uuid).one_or_none()

    def get_all(self):
        return self.db.query(self.model).all()

    def filter(
        self,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_order: str | None,
        search: str | None
    ) -> Tuple[List, int]:
        query = self.db.query(self.model)

        query = self.apply_search(query, search)

        if sort_by:
            sort_col = getattr(self.model, sort_by, None)
            if sort_col is not None:
                query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())

        total = query.count()
        data = query.offset((page - 1) * page_size).limit(page_size).all()

        return data, total
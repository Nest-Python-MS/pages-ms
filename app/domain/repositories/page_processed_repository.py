from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.domain.models.page_model import PageProcessedData
from sqlalchemy.exc import SQLAlchemyError


class PageProcessedRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data):
        try:
            processed = PageProcessedData(**data)
            self.db.add(processed)
            self.db.commit()
            self.db.refresh(processed)
            return processed
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_one(self, id: int):
        return self.db.query(PageProcessedData).filter(PageProcessedData.id == id).first()

    def get_all(self):
        return self.db.query(PageProcessedData).all()

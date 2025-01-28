from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.domain.models.page_model import PageStagingLog
from sqlalchemy.exc import SQLAlchemyError


class PageLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data):
        try:
            log = PageStagingLog(**data)
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_one(self, id: int):
        return self.db.query(PageStagingLog).filter(PageStagingLog.id == id).first()

    def get_all(self):
        return self.db.query(PageStagingLog).all()

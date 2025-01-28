from fastapi import HTTPException
from sqlalchemy import Numeric, and_, cast, func
from sqlalchemy.orm import Session
from app.domain.models.page_model import PageStagingData, PageProcessedData
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from app.core.database import engine


class PageRepository:
    def __init__(self, db: Session):
        self.db = db
        self.engine = engine

    def create(self, data):
        try:
            db_page = PageStagingData(**data)
            self.db.add(db_page)
            self.db.commit()
            self.db.refresh(db_page)
            return db_page
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_one(self, id: int):
        return self.db.query(PageStagingData).filter(PageStagingData.id == id).first()

    def get_all(self):
        return self.db.query(PageStagingData).all()
    
    def exists_in_date(self, platform_id: int, date : str):
        return self.db.query(PageStagingData).filter(and_(
            PageStagingData.date == date,
            PageStagingData.platform_id == platform_id
        )).first()
    
    def get_all_pending(self, date : str):
        return self.db.query(PageStagingData).filter(and_(
            PageStagingData.date == date,
            PageStagingData.status == "pending"
        )).all()
    
    def get_staging_from_date(self, date : str):
        return self.db.query(PageStagingData).filter(and_(
            PageStagingData.date == date,
        )).all()
    
    def insert_bulk_data(self, data_dict : dict):
        chunksize = 100
        for i in range(0, len(data_dict), chunksize):
            self.db.bulk_insert_mappings(PageProcessedData, data_dict[i:i+chunksize])
            self.db.commit()

        return True  

    def change_staging_status(self, id : int, status : str ,output_path : str = None ):

        record = self.db.query(PageStagingData).filter(PageStagingData.id == id).first()

        if record:
            record.status = status
            if output_path is None:
                record.file_path_processed = output_path
            
            self.db.commit()
            return True
        else:
            return False

    def total_amount_month(self, year , month):
        total_amount = self.db.query(func.sum(cast(PageProcessedData.amount, Numeric))).filter(
            and_(
                PageStagingData.date.like(f"{year}-{month:02d}%")
            )
        ).scalar()

        return total_amount or 0 

from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SQLAlchemyEnum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class StatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUEST_ERROR = "request_error"

class PageStagingData(Base):
    __tablename__ = "page_staging_data"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_path_processed = Column(String, nullable=True)
    date = Column(String, nullable=False)
    platform_id = Column(Integer, nullable=False)
    status = Column(SQLAlchemyEnum(StatusEnum), nullable=False, default=StatusEnum.PENDING)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    logs = relationship("PageStagingLog", back_populates="staging_data")
    processed_data = relationship("PageProcessedData", back_populates="staging_data")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "platform_id": self.platform_id,
            "status": self.status,
        }

class PageStagingLog(Base):
    __tablename__ = "page_staging_log"

    id = Column(Integer, primary_key=True, index=True)
    staging_data_id = Column(Integer, ForeignKey("page_staging_data.id"), nullable=False)
    error_description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    staging_data = relationship("PageStagingData", back_populates="logs")


class PageProcessedData(Base):
    __tablename__ = "page_processed_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    staging_data_id = Column(Integer, ForeignKey("page_staging_data.id"), nullable=False)
    model_name = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    staging_data = relationship("PageStagingData", back_populates="processed_data")

from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class StagingDataStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUEST_ERROR = "request_error"

class StagingDataSchema(BaseModel):
    file_path: str
    date: str
    status: StagingDataStatusEnum

class SaveToDataLakeSchema(BaseModel):
    date: str
    page_id: int

class ProcessingDataSchema(BaseModel):
    date: str

class StagingDataResponseSchema(StagingDataSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
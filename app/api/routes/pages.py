from fastapi import APIRouter, Depends, HTTPException
import requests
from app.services.page_service import PageService
from app.domain.schemas.page_schema import SaveToDataLakeSchema, StagingDataResponseSchema, StagingDataSchema, ProcessingDataSchema
from app.domain.repositories.page_repository import PageRepository
from app.domain.repositories.page_log_repository import PageLogRepository
from app.domain.repositories.page_processed_repository import PageProcessedRepository
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.config.nats_service import nats_client

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency para inicializar el repositorio
def get_page_repository(db: Session = Depends(get_db)) -> PageRepository:
    return PageRepository(db) 

def get_page_log_repository(db: Session = Depends(get_db)) -> PageLogRepository:
    return PageLogRepository(db) 

def get_page_processed_repository(db: Session = Depends(get_db)) -> PageProcessedRepository:
    return PageProcessedRepository(db) 

def get_page_service(page_staging: PageRepository = Depends(get_page_repository), 
                     page_log: PageLogRepository = Depends(get_page_log_repository),
                     page_processed: PageProcessedRepository = Depends(get_page_processed_repository)):
    return PageService(page_staging, page_log, page_processed)

@router.post("/pages/", response_model=StagingDataResponseSchema, summary="Create a new page", description="Creates a new page staging data record")
def create_page(
    data: StagingDataSchema,
    page_service: PageService = Depends(get_page_service)
):
    return page_service.create(data)

@router.get("/pages/{id}", response_model=StagingDataResponseSchema)
def get_page(id: int, page_service: PageService = Depends(get_page_service)):
    page = page_service.get_one(id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.get("/pages/", response_model=list[StagingDataResponseSchema])
def get_all_pages(page_service: PageService = Depends(get_page_service)):
    return page_service.get_all()

@router.post("/pages/save_to_data_lake", response_model=StagingDataResponseSchema)
def save_to_data_lake(data: SaveToDataLakeSchema, page_service: PageService = Depends(get_page_service)):
    try:
        result = page_service.save_to_data_lake(data)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except requests.exceptions.RequestException as re:
        raise HTTPException(status_code=502, detail=f"Error while connecting to external API: {str(re)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@router.post("/pages/processing_data", response_model=list[StagingDataSchema])
def processing_data(data: ProcessingDataSchema, page_service: PageService = Depends(get_page_service)):
    try:
        result = page_service.processing_data(data)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")   

@router.post("/api/pages/test")
async def test_nats():
    await nats_client.publish("pages_test", "llega")
    return {"message": "Mensaje enviado a NATS"}        

import json
import asyncio
from nats.aio.client import Client as NATS
from fastapi import FastAPI
import requests
from app.config.settings import NATS_URL
from nats.aio.msg import Msg
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.domain.repositories.page_repository import PageRepository
from app.domain.repositories.page_log_repository import PageLogRepository
from app.domain.repositories.page_processed_repository import PageProcessedRepository
from app.services.page_service import PageService

app = FastAPI()

nats_client = NATS()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Creación de los repositorios
def get_page_repository(db: Session) -> PageRepository:
    return PageRepository(db)

def get_page_log_repository(db: Session) -> PageLogRepository:
    return PageLogRepository(db)

def get_page_processed_repository(db: Session) -> PageProcessedRepository:
    return PageProcessedRepository(db)

# Instanciación de PageService
def get_page_service(db: Session) -> PageService:
    page_repository = get_page_repository(db)
    page_log_repository = get_page_log_repository(db)
    page_processed_repository = get_page_processed_repository(db)
    return PageService(page_repository, page_log_repository, page_processed_repository)

# Conexión con NATS
async def connect_nats():
    await nats_client.connect(NATS_URL)
    print("Conectado al servidor NATS")

async def close_nats():
    await nats_client.close()

# Manejador del mensaje para 'test_nats'
async def handle_test_nats(msg: Msg):
    print(f"Mensaje recibido en 'test_nats': {msg.data.decode()}")
    test = {"id": 1, "name": "Test OK !!!"}
    res = {
        "status": 200,
        "message": "Success",
        "data": test
    }

    test_json = json.dumps(res)
    await nats_client.publish(msg.reply, test_json.encode())

# Manejador del mensaje para 'get_all_pages'
async def handle_get_all_pages(msg: Msg):
    db = next(get_db())
    page_service = get_page_service(db)

    data = page_service.get_all()
    data_serializable = [item.to_dict() for item in data]
    res = {
        "status": 200,
        "message": "Success",
        "data": data_serializable
    }
    data_json = json.dumps(res)
    await nats_client.publish(msg.reply, data_json.encode())

async def handle_total_amount_month(msg: Msg):
    db = next(get_db())
    page_service = get_page_service(db)

    data = page_service.total_amount_month()
    data_serializable = json.dumps(float(data))
    res = {
        "status": 200,
        "message": "Success",
        "data": data_serializable
    }
    data_json = json.dumps(res)
    await nats_client.publish(msg.reply, data_json.encode())    

async def handle_get_staging_from_date(msg: Msg):
    db = next(get_db())
    page_service = get_page_service(db)
    received_data = json.loads(msg.data.decode())
    params = received_data.get('data', None)
    if params and 'date' in params:
        date = params['date']
        data = page_service.get_staging_from_date(date)
        
        data_serializable = [item.to_dict() for item in data]
        res = {
            "status": 200,
            "message": "Success",
            "data": data_serializable
        }
    else:
        res = {
            "status": 400,
            "message": "Missing or invalid 'date' in the parameters"
        }

    data_json = json.dumps(res)
    await nats_client.publish(msg.reply, data_json.encode())   
    
async def handle_processing_data(msg: Msg):
    db = next(get_db())
    page_service = get_page_service(db)
    received_data = json.loads(msg.data.decode())
    params = received_data.get('data', None)
    if params and 'date' in params:
        date = params['date']
        data = page_service.processing_data(date)
        
        data_serializable = [item.to_dict() for item in data]
        res = {
            "status": 200,
            "message": "Success",
            "data": data_serializable
        }
    else:
        res = {
            "status": 400,
            "message": "Missing or invalid 'date' in the parameters"
        }

    data_json = json.dumps(res)
    await nats_client.publish(msg.reply, data_json.encode())

async def handle_save_to_data_lake(msg: Msg):
    db = next(get_db())
    page_service = get_page_service(db)

    received_data = json.loads(msg.data.decode())
    params = received_data.get('data', None)

    if params and 'date' in params and 'page_id' in params:
        request_params = {
            "date": params['date'],
            "page_id": params['page_id']
        }

        try:
            data = page_service.save_to_data_lake(request_params)
            data_serializable = [data.to_dict()]

            res = {
                "status": 200,
                "message": "Success",
                "data": data_serializable
            }
        except ValueError as e:
            # Captura de ValueError (si el registro ya existe)
            res = {
                "status": 400,
                "message": f"Error: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            # Captura de errores de red o problemas con la API
            res = {
                "status": 500,
                "message": f"API request failed: {str(e)}"
            }
        except Exception as e:
            # Captura de cualquier otro error inesperado
            res = {
                "status": 500,
                "message": f"Unexpected error: {str(e)}"
            }
    else:
        res = {
            "status": 400,
            "message": "Missing or invalid 'date' or 'page_id' in the parameters"
        }

    data_json = json.dumps(res)
    await nats_client.publish(msg.reply, data_json.encode())

# Escucha de los mensajes de NATS
async def listen_to_nats():
    await nats_client.subscribe("test_nats", cb=handle_test_nats)
    await nats_client.subscribe("get_all_pages", cb=handle_get_all_pages)
    await nats_client.subscribe("processing_data", cb=handle_processing_data)
    await nats_client.subscribe("save_to_data_lake", cb=handle_save_to_data_lake)
    await nats_client.subscribe("get_staging_from_date", cb=handle_get_staging_from_date)
    await nats_client.subscribe("total_amount_month", cb=handle_total_amount_month)

# Manejo de eventos de inicio y cierre de la aplicación
app.add_event_handler("startup", connect_nats)
app.add_event_handler("startup", listen_to_nats)
app.add_event_handler("shutdown", close_nats)

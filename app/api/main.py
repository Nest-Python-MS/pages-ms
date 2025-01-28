from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import pages
from app.config.nats_service import nats_client, connect_nats, close_nats, listen_to_nats

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectar a NATS en el inicio
    await connect_nats()
    print("NATS conectado en el inicio")
    
    # Iniciar el listener para escuchar mensajes
    await listen_to_nats()

    yield  # Mantener la aplicación en ejecución

    # Cerrar la conexión de NATS al cerrar la aplicación
    await close_nats()
    print("NATS desconectado en el apagado")

# Inicialización de la aplicación FastAPI
app = FastAPI(debug=True, lifespan=lifespan)

print("App initialized successfully")

# Incluye los enrutadores
# app.include_router(pages.router, prefix="", tags=["pages"])
# print("Router included successfully")
